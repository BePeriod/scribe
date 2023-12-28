import pytest

import scribe
from scribe.text import text


def test_transcribe_non_existent_file():
    with pytest.raises(FileNotFoundError):
        text.transcribe("/not/a/real/path.ogg")


def test_transcribe_invalid_file():
    with pytest.raises(RuntimeError):
        not_audio = scribe.path_from_root("../test/resources/not_audio.txt")
        text.transcribe(str(not_audio.absolute()))


def test_transcribe_recording():
    file = scribe.path_from_root("../test/resources/voice_recording.ogg")
    transcription = text.transcribe(str(file.absolute()))
    assert transcription == "This is a test recording."


def test_pseudo_translation():
    # pyproject.toml set the pseudo translate setting to on.
    # testing DeepL would require an API key.
    raw = "<p>This <em>is</em> a <strong>test</strong>.</p>"
    translated = text.translate(raw, "pt")
    assert translated == "<p>THIS <em>IS</em> A <strong>TEST</strong>.</p>"
