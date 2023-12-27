"""
This package contains global configuration functionality for the app.

Modules
----------
settings: Environment variables
logs: Logging configuration

"""
import os
import time

from scribe.config import logs


def init():
    """
    Configure the server to UTC and initialize the logging configuration.
    :return: None
    """
    os.environ["TZ"] = "UTC"
    time.tzset()
    logs.init()
