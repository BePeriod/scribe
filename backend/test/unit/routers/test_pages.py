import scribe
from scribe.models.models import Recording, User


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


def test_upload_invalid_file(api_client, user_session):
    not_audio = scribe.path_from_root("../test/resources/not_audio.txt")
    api_client.cookies.set("scribe_session_id", user_session.id)
    with open(not_audio, "rb") as file:
        response = api_client.post("/upload", files={"audio_file": file})
        assert response.status_code == 415


def test_upload_audio_file(api_client, user_session):
    audio = scribe.path_from_root("../test/resources/voice_recording.ogg")
    api_client.cookies.set("scribe_session_id", user_session.id)
    with open(audio, "rb") as file:
        response = api_client.post("/upload", files={"audio_file": file})
        assert response.status_code == 303
        assert (
            response.headers["Content-Type"]
            == "text/vnd.turbo-stream.html; charset=utf-8"
        )
        assert "Processing audio..." in response.text


def test_transcribe_nonexistent_file(api_client, user_session):
    api_client.cookies.set("scribe_session_id", user_session.id)
    response = api_client.get("/recordings/123")
    assert response.status_code == 404


def test_transcribe_file(api_client, user_session):
    api_client.cookies.set("scribe_session_id", user_session.id)
    audio_file = scribe.path_from_root("../test/resources/voice_recording.ogg")
    recording = Recording(id="123", file_path=str(audio_file))
    user_session.set("recordings", {"123": recording})
    response = api_client.get("/recordings/123")
    assert "This is a test recording." in response.text
