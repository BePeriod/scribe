import logging
from typing import Annotated

from fastapi import Depends
from starlette.requests import Request

from scribe.exceptions import NotAuthenticatedException
from scribe.models.models import User
from scribe.session.session import Session
from scribe.session.session import SessionStore

session_store = SessionStore()


def get_session(request: Request) -> Session:
    session = None
    try:
        session = request.state.session
    except AttributeError:
        session_id = request.cookies.get("scribe_session_id")
        if session_id is not None:
            try:
                session = session_store.get_session(session_id)
            except AttributeError:
                logging.info("invalid session id")

    if not session:
        session = session_store.start_session()

    request.state.session = session

    return request.state.session


def session_user(session: Annotated[Session, Depends(get_session)]) -> User:
    user = session.get("user")
    if user is None:
        raise NotAuthenticatedException("Not authenticated")

    return user
