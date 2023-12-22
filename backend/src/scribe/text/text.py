import re
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
    if settings.PSEUDO_TRANSLATE:
        return _pseudo_translation(text)

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


def _pseudo_translation(text: str) -> str:
    # This regex is split into two capture groups to handle xml tags differently.
    # <[^>]+> captures xml tags into the tag group
    # [^<]+ captures everything else into the text group
    return re.sub(r"(?P<tag><[^>]+>)|(?P<text>[^<]+)", _pseudo_replace, text)


def _pseudo_replace(m):
    g = m.group("text")
    if g is None:
        return m.group()
    return g.upper()
