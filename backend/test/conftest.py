import secrets

import pytest
from fastapi.testclient import TestClient
from starlette.datastructures import Headers
from starlette.requests import Request

import scribe.dependencies
import scribe.slack.slack
from scribe.main import app
from scribe.models.models import Channel, Team, User
from scribe.session.session import SessionStore

from . import mocks

_session_store = SessionStore()


def pytest_addoption(parser):
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="run integration tests",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "integration: mark test as integration test")


def pytest_collection_modifyitems(config, items):
    """
    Integration tests needing 3rd party credentials will not be run by default.
    Passing the --run-integration flag will run them.

    :param config:
    :param items:
    :return: None
    """
    if config.getoption("--run-integration"):
        # --run-integration given in cli: do not skip integration tests
        return
    skip_integration = pytest.mark.skip(reason="need --run-integration option to run")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)


@pytest.fixture(autouse=True)
def global_mocks(mocker):
    mocker.patch.object(scribe.dependencies, "session_store", _session_store)
    mocker.patch.object(scribe.slack.slack, "access_token", mocks.mock_access_token)
    mocker.patch.object(scribe.slack.slack, "SlackClient", mocks.MockSlackClient)


@pytest.fixture()
def api_client():
    client = TestClient(app)
    return client


@pytest.fixture()
def user():
    return User(
        id="U1234",
        real_name="John Smith",
        real_name_normalized="John Smith",
        first_name="John",
        last_name="Smith",
        display_name="John Smith",
    )


@pytest.fixture()
def channels():
    return [
        Channel(
            id="U1234",
            name="Channel One",
        )
    ]


@pytest.fixture()
def team():
    return Team(id="T1234", name="The Super Friends")


@pytest.fixture()
def channel():
    return Channel(id="C1234", name="General")


@pytest.fixture()
def access_token(user, team, channel):
    token = secrets.token_urlsafe(16)
    mocks.token_resources[token] = {"user": user, "team": team, "channels": [channel]}
    return token


@pytest.fixture()
def oauth_code(access_token):
    code = secrets.token_urlsafe(16)
    mocks.code_tokens[code] = access_token
    return code


@pytest.fixture()
def session_store():
    return _session_store


@pytest.fixture()
def empty_session(session_store):
    return session_store.start_session()


@pytest.fixture()
def user_session(empty_session, user, channels):
    token = "123456"
    empty_session.set("access_token", token)
    empty_session.set("user", user)
    empty_session.set("channels", channels)

    return empty_session


@pytest.fixture()
def empty_http_request():
    scope = {"type": "http", "headers": Headers()}
    return Request(scope=scope)


@pytest.fixture()
def user_session_http_request(user_session):
    scope = {"type": "http", "headers": Headers(), "state": {"session": user_session}}
    request = Request(scope=scope)
    return request
