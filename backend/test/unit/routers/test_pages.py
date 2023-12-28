from scribe.models.models import User


def test_redirect_to_login(api_client):
    response = api_client.get("/")
    assert response.url.path == "/login"


def test_home_page(api_client, user_session):
    api_client.cookies.set("scribe_session_id", user_session.id)
    response = api_client.get("/")
    assert response.url.path == "/"
    assert "Record your message" in response.text


def test_bad_oauth_state(api_client, empty_session):
    api_client.cookies.set("scribe_session_id", empty_session.id)
    response = api_client.get("/")
    assert response.url.path == "/login"
    assert empty_session.get("state") is not None
    response = api_client.get("/auth/redirect?code=12345&state=ABCDE")
    assert response.status_code == 400
    assert empty_session.get("state") is None


def test_bad_oauth_code(api_client, empty_session):
    bad_code = "1234567890101112"
    api_client.cookies.set("scribe_session_id", empty_session.id)
    api_client.get("/login")
    state = empty_session.get("state")
    response = api_client.get(f"/auth/redirect?code={bad_code}&state={state}")
    assert response.status_code == 401


def test_login_flow(api_client, empty_session, oauth_code):
    api_client.cookies.set("scribe_session_id", empty_session.id)
    api_client.get("/login")
    state = empty_session.get("state")
    response = api_client.get(f"/auth/redirect?code={oauth_code}&state={state}")
    assert response.status_code == 200
    assert response.url.path == "/"
    assert isinstance(empty_session.get("user"), User)
