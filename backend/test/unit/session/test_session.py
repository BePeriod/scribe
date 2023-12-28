from scribe.session.session import SessionStore


def test_create_session():
    store = SessionStore()
    session = store.start_session()
    assert session == store.get_session(session.id)
    assert session.get("unset") is None
    assert session.get("unset", False) is False
    session.set("foo", "bar")
    assert session.get("foo") == "bar"
    session.delete("foo")
    assert session.get("foo") is None
