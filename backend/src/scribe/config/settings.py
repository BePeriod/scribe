"""
The settings module creates a base class of application settings.
Environment variables are read into these settings, falling back on defaults
where properties are not specified.
"""
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    The Settings class extends Pydantic's BaseSettings.

    Attributes
    ----------
    LOG_LEVEL: str
        The logging level for the application: DEBUG | INFO | WARNING | ERROR | CRITICAL
    SITE_URL: STR
        tHE PUBLIC URL of the site
    PORT: int
        The port on which the application is listening
    SESSION_KEY: str
        A unique key to salt the session.
    DEVELOPMENT_MODE: bool
        Flag for if certain debugging behavior is enabled
    DEV_SESSION_ID: str
        When DEVELOPMENT_MODE is enabled,
        this is used to share sessions with ngrok for oAuth logins.
    DEEPL_API_KEY: str
        The api key for translating text with DeepL.
    PSEUDO_TRANSLATE: bool
        Flag to use mock translations instead of DeepL.
    SLACK_AUTH_URL: str
        The Slack authorization URL.
    SLACK_TEAM_ID: str
        The Slack workspace ID.
    SLACK_CLIENT_ID: str
        Slack OAuth client id
    SLACK_CLIENT_SECRET: str
        Slack OAuth client secret
    SLACK_SIGNING_SECRET: str
        Slack JWT signing token
    SLACK_USER_TOKEN: str
        Slack app user token
    SLACK_USER_SCOPES: List[str]
        User scopes to request from Slack
    UPLOAD_PATH: str
        folder path for file uploads
    SOURCE_LANGUAGE: str
        language code for the source language
    TARGET_LANGUAGES: List[str]
        language codes for the target languages
    SLACK_CHANNEL_LANGUAGE_MAP: dict[str, str]
        map of language codes and the Slack channel id
        for where to send messages in that language
    """

    LOG_LEVEL: str = "DEBUG"
    SITE_URL: str = "http://localhost:8000"
    PORT: int = 8000
    SESSION_KEY: str = "some-random-string"
    DEVELOPMENT_MODE: bool = False
    DEV_SESSION_ID: str = "867-5309"
    DEEPL_API_KEY: str = "your-deepl-api-key"
    PSEUDO_TRANSLATE: bool = False
    SLACK_AUTH_URL: str = "https://slack.com/oauth/v2/authorize?scope="
    SLACK_TEAM_ID: str = "your-team-id"
    SLACK_CLIENT_ID: str = "your_client_id"
    SLACK_CLIENT_SECRET: str = "your_client_secret"
    SLACK_SIGNING_SECRET: str = "your_signing_secret"
    SLACK_USER_TOKEN: str = "your_user_token"
    SLACK_USER_SCOPES: List[str] = [
        "channels:read",
        "chat:write",
        "identify",
        "pins:write",
        "team:read",
        "users.profile:read",
    ]
    UPLOAD_PATH: str = "/tmp/scribe"
    SOURCE_LANGUAGE: str = "en"
    TARGET_LANGUAGES: list[str] = ["es", "fr", "it", "ru", "pt"]
    SLACK_CHANNEL_LANGUAGE_MAP: dict[str, str] = {}

    class Config:
        env_prefix = "SCRIBE_"
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
