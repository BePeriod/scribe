from starlette.datastructures import State
import secrets
from scribe.config.settings import settings


class Session:
    def __init__(self, session_id: str):
        self.id = session_id
        self._state = State()

    def get(self, key: str, default=None):
        return getattr(self._state, key, default)

    def set(self, key: str, value):
        setattr(self._state, key, value)

    def delete(self, key: str):
        try:
            delattr(self._state, key)
        except KeyError:
            pass


class SessionStore:
    def __init__(self):
        self._state = State()

    def start_session(self) -> Session:
        session_id = self._generate_id()
        session = Session(session_id)
        setattr(self._state, session_id, session)

        return session

    def get_session(self, session_id: str) -> Session:
        return getattr(self._state, session_id)

    @staticmethod
    def _generate_id() -> str:
        if settings.DEVELOPMENT_MODE:
            # needed for sharing session id with ngrok for Oauth client credentials flow
            return settings.DEV_SESSION_ID

        return secrets.token_urlsafe(16)
