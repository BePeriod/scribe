from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    LOG_LEVEL: str = "DEBUG"
    SITE_URL: str = "http://localhost:8000"
    PORT: int = 8000
    SESSION_KEY: str = "some-random-string"
    DEVELOPMENT_MODE: bool = False
    DEV_SESSION_ID: str = "867-5309"
    DEEPL_API_KEY: str = "your-deepl-api-key"
    PSEUDO_TRANSLATE: bool = False
    SLACK_AUTH_URL: str = "https://slack.com/openid/connect/authorize"
    SLACK_TOKEN_URL: str = "https://slack.com/api/openid.connect.token"
    SLACK_CLIENT_ID: str = "your_client_id"
    SLACK_CLIENT_SECRET: str = "your_client_secret"
    SLACK_SIGNING_SECRET: str = "your_signing_secret"
    SLACK_BOT_TOKEN: str = "your_bot_token"
    SLACK_USER_TOKEN: str = "your_user_token"
    USER_SCOPES: List[str] = ["openid"]
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
