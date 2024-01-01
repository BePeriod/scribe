"""
This module provides classes for in-memory session management.
"""
import secrets

from starlette.datastructures import State

from scribe.config.settings import settings


class Session:
    """
    This class provides stores session state in-memory.
    """

    def __init__(self, session_id: str):
        self.id = session_id
        self._state = State()

    def get(self, key: str, default=None):
        """
        Get a value from the session state

        :param key: the property key
        :param default: the default value if key does not exist
        :return: the stored value for the key or the default value
        """
        return getattr(self._state, key, default)

    def set(self, key: str, value):
        """
        Set a value on the session state
        :param key: the property key
        :param value: the value to set
        :return: None
        """
        setattr(self._state, key, value)

    def append(self, key: str, value):
        """
        Append a value on the session property.
        If the property does not exist, it will be created.
        :param key: the property key
        :param value: the value to set
        :return: None
        """
        current = self.get(key, [])
        if not isinstance(current, list):
            raise ValueError("existing value is not list")

        value = [value] if isinstance(value, str) else value
        if not isinstance(value, list):
            raise ValueError("value is not list or string")

        self.set(key, current + value)

    def delete(self, key: str):
        """
        Delete a value from the session state
        :param key: the property key
        :return: None
        """
        try:
            delattr(self._state, key)
        except KeyError:
            pass

    def consume(self, key: str, default=None):
        """
        Get a session property then delete it.
        :param key:
        :param default:
        :return: Any
        """
        value = self.get(key, default)
        self.delete(key)
        return value


class SessionStore:
    """
    This class stores all active sessions in-memory
    """

    def __init__(self):
        self._state = State()

    def start_session(self) -> Session:
        """
        Start a new Session
        :return: the new Session object
        """
        session_id = self._generate_id()
        session = Session(session_id)
        setattr(self._state, session_id, session)

        return session

    def get_session(self, session_id: str) -> Session:
        """
        Get a Session object by id
        :param session_id: the session id
        :return: Session object
        """
        return getattr(self._state, session_id)

    @staticmethod
    def _generate_id() -> str:
        """
        Generate a unique session id
        :return: string
        """
        if settings.DEVELOPMENT_MODE:
            # needed for sharing session id with ngrok for OAuth client credentials flow
            return settings.DEV_SESSION_ID

        return secrets.token_urlsafe(16)
