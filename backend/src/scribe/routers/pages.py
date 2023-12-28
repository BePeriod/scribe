"""
This module contains all the HTML based routes for the app.
"""
import datetime
import logging
import os
import secrets
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sse_starlette.sse import EventSourceResponse
from starlette import status
from starlette.responses import RedirectResponse

from scribe.config.settings import settings
from scribe.dependencies import get_session, session_user, slack_client
from scribe.models.models import Recording, User
from scribe.session.session import Session
from scribe.slack import slack
from scribe.slack.slack import SlackClient, SlackError
from scribe.text import text

# initialize the frontend router
router = APIRouter()

# configure the template engine
_templates = Jinja2Templates(directory="templates")
_templates.env.globals["now"] = datetime.datetime.utcnow()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, user: Annotated[str, Depends(session_user)]):
    """
    Renders the home page

    :param request: The request object
    :param user: The logged in user
    :return: HTML Response
    """

    return _templates.TemplateResponse(
        "pages/home.html.j2", {"request": request, "user": user}
    )


@router.get("/login", response_class=HTMLResponse)
async def login(request: Request, session: Annotated[Session, Depends(get_session)]):
    """
    Renders the login page

    :param request: The HTTP Request
    :param session: The active Session object
    :return: HTML Response
    """

    state = secrets.token_urlsafe(16)
    session.set("state", state)
    nonce = secrets.token_urlsafe(16)
    session.set("nonce", nonce)

    auth_link = (
        f"{settings.SLACK_AUTH_URL}?scope="
        f"&user_scope={ ','.join(settings.SLACK_USER_SCOPES) }"
        f"&response_type=code"
        f"&state={ state }"
        f"&nonce={ nonce }"
        f"&redirect_uri={slack.redirect_uri}"
        f"&team={settings.SLACK_TEAM_ID}"
        f"&client_id={settings.SLACK_CLIENT_ID}"
    )

    return _templates.TemplateResponse(
        "pages/login.html.j2",
        {"request": request, "auth_link": auth_link},
    )


@router.get("/auth/redirect")
async def read_code(
    code: str,
    state: str,
    session: Annotated[Session, Depends(get_session)],
):
    """
    Convert OAuth code to access token and redirect to home page.

    :param code: The OAuth code returned by Slack
    :param state: The state variable sent in the auth request
    :param session: The active Session object
    :return: RedirectResponse
    """
    session_state = session.get("state")
    if not session_state or session_state != state:
        session.delete("state")
        session.delete("nonce")

        raise HTTPException(status_code=400, detail="Invalid state")

    try:
        access_token = slack.access_token(code)
        client = slack.SlackClient(access_token)
        # todo make calls asynchronously
        session.set("access_token", access_token)
        session.set("user", client.user())
        session.set("team", client.team())
        session.set("channels", client.channels())

        return RedirectResponse("/")
    except SlackError as err:
        logging.warning(f"Invalid token: {err}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as err:
        logging.debug(f"uncaught exception: {err}")
        raise err
    finally:
        session.delete("state")
        session.delete("nonce")


async def transcription_event_generator(request: Request, recording: Recording):
    """
    Server Side Event Generator: Transcribes a recording and sends a message when done.
    :param request: The HTTP Request
    :param recording: The audo recording to transcribe
    :returns: a message dict with a turbo stream for updating the UI
    """
    while True:
        if await request.is_disconnected():
            logging.debug("Request disconnected")
            break

        try:
            recording.transcription = text.transcribe(recording.file_path)
            logging.debug("Transcription completed. Disconnecting now")
            data = _templates.get_template(
                "streams/transcription_complete.html.j2"
            ).render({"request": request, "recording": recording})
            yield {"event": "message", "data": data}
        except RuntimeError as err:
            logging.warning(f"error transcribing audio: {err}")
            yield {"event": "error", "data": err}
        break


@router.post("/upload")
async def upload(
    audio_file: UploadFile,
    request: Request,
    _user: Annotated[User, Depends(session_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """
    upload an audio file
    :param audio_file: mpeg, ogg, wan, or flac audio file
    :param request: the HTTP request
    :param _user: logged in user, used to check user session exists
    :param session: the active Session object
    :return: HTML Response
    """
    allowed_mime_types = ["audio/mpeg", "audio/ogg", "audio/wav", "audio/flac"]
    if audio_file.content_type not in allowed_mime_types:
        logging.warning(f"invalid content-type: {audio_file.content_type}")
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Unsupported file format"
        )

    file_id = uuid4()
    parent_dir = os.path.join(settings.UPLOAD_PATH, session.id)
    Path(parent_dir).mkdir(parents=True, exist_ok=True)
    file_path = os.path.join(parent_dir, f"{file_id }.ogg")

    file_content = await audio_file.read()
    # Save the content to the file
    with open(file_path, "wb") as f:
        f.write(file_content)

    recording = Recording(id=str(file_id), file_path=file_path)
    recordings = session.get("recordings", {})
    recordings[recording.id] = recording
    session.set("recordings", recordings)

    return _templates.TemplateResponse(
        "streams/upload_audio.html.j2",
        {"request": request, "recording": recording},
        # Turbo needs post data that returns HTML to set a status of 303 redirect.
        # This is due to how browsers handle page history with form submissions.
        status_code=303,
        headers={"Content-Type": "text/vnd.turbo-stream.html; charset=utf-8"},
    )


@router.get("/recordings/{recording_id}")
async def transcribe_recording(
    request: Request,
    recording_id: str,
    _user: Annotated[User, Depends(session_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """
    Transcribe an audio recording

    :param request: the HTTP request object
    :param recording_id: The id of the audio recording
    :param _user: active session user
    :param session: active Session object
    :return: SSE EventSourceResponse
    """
    recordings = session.get("recordings", {})
    recording = recordings.get(recording_id, None)
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    event_generator = transcription_event_generator(request, recording)

    return EventSourceResponse(
        event_generator,
        headers={"Content-Type": "text/event-stream"},
    )


@router.post("/publish")
async def publish(
    formatted_message: Annotated[str, Form()],
    request: Request,
    _user: Annotated[User, Depends(session_user)],
    client: Annotated[SlackClient, Depends(slack_client)],
    pin_to_channel: Annotated[bool, Form()] = False,
):
    """
    Translate a message and publish it to each language channel.

    :param formatted_message: message formatted as HTML
    :param request: the http request
    :param _user: active session user
    :param client: SlackClient object
    :param pin_to_channel: flag for pinning messages to Slack channels
    :return: HTML Response
    """
    message = formatted_message.strip()
    for target in settings.TARGET_LANGUAGES:
        translated = text.translate(message, target)
        client.publish(translated, target, pin_to_channel)

    client.publish(message, settings.SOURCE_LANGUAGE, pin_to_channel)

    return _templates.TemplateResponse(
        "streams/message_published.html.j2",
        {"request": request},
        status_code=303,
        headers={"Content-Type": "text/vnd.turbo-stream.html; charset=utf-8"},
    )
