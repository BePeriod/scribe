from typing import Callable


import whisper


from scribe.models.models import Recording

model = whisper.load_model("base")

_listeners = []


def subscribe(callback: Callable[[Recording], None]):
    _listeners.append(callback)


async def transcribe(recording: Recording) -> str:
    result = await model.Transcribe(recording.file_path)
    recording.transcription = result["text"]
    return recording.transcription
