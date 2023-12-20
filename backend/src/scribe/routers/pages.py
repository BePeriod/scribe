import datetime
import logging
import os
import secrets
import tempfile
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sse_starlette.sse import EventSourceResponse
from starlette import status
from starlette.responses import RedirectResponse

from scribe.config.settings import settings
from scribe.dependencies import get_session, session_user
from scribe.models.models import Recording, User
from scribe.session.session import Session
from scribe.slack import slack
from scribe.text.transcription import transcribe

# initialize the frontend router
router = APIRouter()

# configure the template engine
_templates = Jinja2Templates(directory="templates")
_templates.env.globals["now"] = datetime.datetime.utcnow()


# define the home page route
@router.get("/", response_class=HTMLResponse)
async def home(request: Request, user: Annotated[str, Depends(session_user)]):
    # render the template file in /templates/home.html
    # we are not currently using this request object
    return _templates.TemplateResponse(
        "pages/home.html.j2", {"request": request, "user": user}
    )


@router.get("/login", response_class=HTMLResponse)
async def login(request: Request, session: Annotated[Session, Depends(get_session)]):
    state = secrets.token_urlsafe(16)
    session.set("state", state)
    nonce = secrets.token_urlsafe(16)
    session.set("nonce", nonce)
    auth_link = (
        f"{settings.SLACK_AUTH_URL}?scope={'%20'.join(settings.USER_SCOPES)}"
        f"&response_type=code"
        f"&state={ state }"
        f"&nonce={ nonce }"
        f"&redirect_uri={slack.redirect_uri}"
        f"&client_id={settings.SLACK_CLIENT_ID}"
    )

    return _templates.TemplateResponse(
        "pages/login.html.j2", {"request": request, "auth_link": auth_link}
    )


@router.get("/auth/redirect")
async def read_code(
    code: str,
    state: str,
    session: Annotated[Session, Depends(get_session)],
):
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
    except ValueError as err:
        logging.warning(f"Invalid token: {err}")
        raise HTTPException(status_code=400, detail="Invalid token")
    except Exception as err:
        logging.debug(f"uncaught exception: {err}")
        raise err
    finally:
        session.delete("state")
        session.delete("nonce")


async def transcription_event_generator(request: Request, recording: Recording):
    while True:
        if await request.is_disconnected():
            logging.debug("Request disconnected")
            break

        text = await transcribe(recording)
        logging.debug("Transcription completed. Disconnecting now")
        data = _templates.TemplateResponse(
            "streams/transcription.html.j2",
            {"request": request, "text": text},
        )
        yield {"event": "end", "data": data}
        break


def audio_upload(content_type: str = Header(...)):
    """Require request MIME-type to be application/vnd.api+json"""

    # flac, mp3, mp4, mpeg, mpga, m4a, ogg, wav, or webm.
    allowed_mime_types = ["audio/mpeg", "audio/ogg", "audio/wav", "audio/flac"]

    if content_type not in allowed_mime_types:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Unsupported media type: {content_type}."
            f" It must be one of these types: {', '.join(allowed_mime_types)}",
        )


@router.post("/upload")
async def upload(
    audio_file: UploadFile,
    request: Request,
    _user: Annotated[User, Depends(session_user)],
    session: Annotated[Session, Depends(get_session)],
):
    allowed_mime_types = ["audio/mpeg", "audio/ogg", "audio/wav", "audio/flac"]
    if audio_file.content_type not in allowed_mime_types:
        logging.warning(f"invalid content-type: {audio_file.content_type}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Unsupported file format")

    file_id = uuid4()
    temp_dir = tempfile.TemporaryDirectory()

    file_content = await audio_file.read()
    parent_dir = os.path.join(temp_dir.name, session.id)
    Path(parent_dir).mkdir(parents=True, exist_ok=True)
    file_path = os.path.join(parent_dir, f"{file_id }.ogg")

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
    recordings = session.get("recordings", {})
    recording = recordings.get(recording_id, None)
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    event_generator = transcription_event_generator(request, recording)

    return EventSourceResponse(event_generator)
