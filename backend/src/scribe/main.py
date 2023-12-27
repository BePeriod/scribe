"""
This is the main entry point for the scribe.

This initializes configuration settings and creates the FastAPI instance.
"""

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from starlette import status
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse

from scribe import config
from scribe.config.settings import settings
from scribe.dependencies import get_session
from scribe.exceptions import NotAuthenticatedException
from scribe.routers import pages

config.init()
logging.info(f"starting the server on port {settings.PORT}...")

# initialize FastAPI
app = FastAPI(debug=settings.DEVELOPMENT_MODE)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_KEY,
    session_cookie="scribe_session_id",
)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(pages.router)


@app.middleware("http")
async def session_middleware(request: Request, call_next):
    """
    Middleware that initializes the session if it doesn't exist.
    :param request: The Request object
    :param call_next: The next function to call
    :return: an HTTP Response object
    """
    session = get_session(request)
    response = await call_next(request)
    response.set_cookie(key="scribe_session_id", value=session.id, httponly=True)
    return response


@app.exception_handler(NotAuthenticatedException)
def auth_exception_handler(request: Request, _exc: NotAuthenticatedException):
    """
    Exception handler called when authentication fails.
    For API calls, a 401 is returned.
    For page views, the user is redirected to the login page.
    :param request: The Request object
    :param _exc: The exception object
    :return: RedirectResponse to login page
    """
    if request.url.path.startswith("/api"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    return RedirectResponse(url="/login")
