from typing import Callable

import deepl
import whisper

from scribe.config.settings import settings
from scribe.models.models import Recording

model = whisper.load_model("base")

_listeners = []

_translator = deepl.Translator(settings.DEEPL_API_KEY)


def subscribe(callback: Callable[[Recording], None]):
    _listeners.append(callback)


def transcribe(file_path: str) -> str:
    result = model.transcribe(file_path)
    return result["text"]


def translate(text: str, target_language: str) -> str:
    source_code = settings.SOURCE_LANGUAGE.upper()
    if target_language == "en":
        target_code = "EN-US"
    elif target_language == "pt":
        target_code = "PT-BR"
    else:
        target_code = target_language.upper()

    return _translator.translate_text(
        text, target_lang=target_code, source_lang=source_code, tag_handling="html"
    ).text
