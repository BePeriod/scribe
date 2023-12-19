import datetime
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from scribe.auth import auth
from scribe.config.settings import settings
from scribe.dependencies import session_user, get_session
from scribe.session.session import Session
from scribe.slack import slack

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
    state = auth.secret()
    session.set("state", state)
    nonce = auth.secret()
    session.set("nonce", nonce)
    auth_link = (
        f"{settings.SLACK_AUTH_URL}?scope={'%20'.join(settings.USER_SCOPES)}"
        f"&response_type=code"
        f"&state={ state }"
        f"&nonce={ nonce }"
        f"&redirect_uri={auth.redirect_uri}"
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
