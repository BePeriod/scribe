from typing import Callable

import whisper

from scribe.models.models import Recording

model = whisper.load_model("base")

_listeners = []


def subscribe(callback: Callable[[Recording], None]):
    _listeners.append(callback)


def transcribe(file_path: str) -> str:
    result = model.transcribe(file_path)
    return result["text"]


def translate(text: str, target: str) -> str:
    return f"{text}:{target}"
