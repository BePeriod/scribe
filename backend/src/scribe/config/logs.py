"""
This module configures logging to format uvicorn messages into stdout.
"""
import logging.config

from scribe.config.settings import settings

ISO_8601 = "%Y-%m-%dT%H:%M:%S%z"

logging_config = {
    "version": 1,  # mandatory field
    # if you want to overwrite existing loggers' configs
    "disable_existing_loggers": True,
    "formatters": {
        "basic": {
            "()": "uvicorn.logging.DefaultFormatter",
            "format": "%(levelprefix)s [%(asctime)s] %(message)s",
            "datefmt": ISO_8601,
        }
    },
    "handlers": {
        "console": {
            "formatter": "basic",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "level": settings.LOG_LEVEL,
        }
    },
    "root": {
        "handlers": ["console"],
        "level": settings.LOG_LEVEL,
    },
}


def init():
    """
    Initialize logging
    :return: None
    """
    logging.config.dictConfig(logging_config)
