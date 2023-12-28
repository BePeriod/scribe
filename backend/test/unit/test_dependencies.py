import pytest

from scribe.dependencies import get_session, session_user, slack_client
from scribe.exceptions import NotAuthenticatedException
from scribe.models.models import User
from scribe.session.session import Session
from scribe.slack.slack import SlackClient


def test_start_new_session(empty_http_request):
    session = get_session(empty_http_request)
    assert isinstance(session, Session)
    assert session.get("user") is None


def test_invalid_session_id(empty_http_request):
    empty_http_request.cookies["scribe_session_id"] = "invalid"
    session = get_session(empty_http_request)
    assert isinstance(session, Session)
    assert session.get("user") is None


def test_cookie_session(empty_http_request, user_session):
    empty_http_request.cookies["scribe_session_id"] = user_session.id
    session = get_session(empty_http_request)
    assert isinstance(session, Session)
    assert session.get("user") is not None
    assert session.get("user") == user_session.get("user")


def test_state_session(user_session_http_request):
    request_session = user_session_http_request.state.session
    session = get_session(user_session_http_request)
    assert session.id == request_session.id
    assert session.get("user") is not None
    assert session.get("user") == request_session.get("user")


def test_unauthenticated_session(empty_http_request):
    with pytest.raises(NotAuthenticatedException):
        session_user(get_session(empty_http_request))


def test_session_user(user_session_http_request):
    user = session_user(get_session(user_session_http_request))
    assert isinstance(user, User)


def test_unauthenticated_slack_client(empty_http_request):
    with pytest.raises(NotAuthenticatedException):
        slack_client(get_session(empty_http_request))


def test_session_slack_client(user_session_http_request):
    client = slack_client(get_session(user_session_http_request))
    assert isinstance(client, SlackClient)
