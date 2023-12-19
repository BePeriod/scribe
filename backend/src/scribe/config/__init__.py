import os
import time

from scribe.config import logs


def init():
    os.environ["TZ"] = "UTC"
    time.tzset()
    logs.init()
