import secrets

from scribe.config.settings import settings

redirect_uri = f"{ settings.SITE_URL }/auth/redirect"


class NotAuthenticatedException(Exception):
    pass


def secret() -> str:
    return secrets.token_urlsafe(16)
