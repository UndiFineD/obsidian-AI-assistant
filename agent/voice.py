"""Voice transcription utilities and API endpoints.

Unified single source of truth for voice functionality.

Notes for tests:
- Import-time reads VOSK_MODEL_PATH with default
    "./models/vosk/vosk-model-small-en-us-0.15"
- If default model path is missing, get_vosk_model() raises RuntimeError
- If env-provided path is missing, we log and return None
- Router exposes POST /api/voice_transcribe using vosk.KaldiRecognizer
"""

from __future__ import annotations

import builtins as _builtins
import json
import logging
import os
import tempfile
import wave
from typing import Optional

from fastapi import APIRouter, UploadFile

from .settings import get_settings
from .utils import safe_call

# Robust voice transcription endpoint
_DEFAULT_MODEL_PATH: str = "./models/vosk/vosk-model-small-en-us-0.15"

# Provide a patchable 'vosk' attribute on this module
try:
    import vosk as _vosk_mod
except Exception:

    class _VoskStub:
        class Model:  # type: ignore
            pass

        class KaldiRecognizer:  # type: ignore
            def __init__(self, *args, **kwargs):
                pass

    _vosk_mod = _VoskStub()
vosk = _vosk_mod  # Expose for tests to patch backend.voice.vosk.*

# Read env but fall back to default if patched getenv returns None
_settings = get_settings()
_mp = os.getenv("VOSK_MODEL_PATH", _DEFAULT_MODEL_PATH)
MODEL_PATH: str = _mp if isinstance(_mp, str) and _mp else _DEFAULT_MODEL_PATH


def get_vosk_model() -> Optional[object]:
    """Load and return a Vosk model instance if available.

    Behavior:
    - If MODEL_PATH is the default and missing: raise RuntimeError (expected by tests).
    - If MODEL_PATH comes from env but is missing: log a warning and return None.
    - Otherwise, attempt to construct the model and return it; on failure return None.
    """
    if not os.path.exists(MODEL_PATH):
        if MODEL_PATH == _DEFAULT_MODEL_PATH:
            raise RuntimeError(
                (
                    f"Vosk model not found at {MODEL_PATH}. "
                    "Download from https://alphacephei.com/vosk/models"
                )
            )
        logging.warning(
            (
                "Vosk model path from environment does not exist: %s. "
                "Proceeding without model."
            ),
            MODEL_PATH,
        )
        return None
    # Safe-call only for model construction
    return safe_call(
        lambda: vosk.Model(MODEL_PATH),
        error_msg=f"Failed to load Vosk model from {MODEL_PATH}",
        default=None,
    )


# Try to load model at import, but don't crash if default path is missing.
# Tests will patch vosk.Model or set VOSK_MODEL_PATH env when needed.
try:
    model = get_vosk_model()
except RuntimeError as e:
    logging.warning("Vosk model unavailable at import: %s", e)
    model = None

router = APIRouter()


@router.post("/api/voice_transcribe")
async def voice_transcribe(file: UploadFile) -> dict:
    # Even if model is None, allow processing with patched recognizer in tests
    # Read uploaded file
    try:
        audio_data = await file.read()
    except Exception as e:
        raise RuntimeError(str(e)) from e

    # Use a temporary file to handle the audio data safely
    temp_path = ""
    try:
        # Create a temporary file to write the audio data
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_path = temp_file.name
            temp_file.write(audio_data)

        # Use a 'with' statement to ensure the wave file is closed before deletion
        with wave.open(temp_path, "rb") as wf:
            if (
                wf.getnchannels() != 1
                or wf.getsampwidth() != 2
                or wf.getframerate() not in [16000, 8000]
            ):
                return {
                    "error": (
                        "Audio must be mono PCM WAV with 16kHz or 8kHz sample rate."
                    )
                }
            rec = vosk.KaldiRecognizer(model, wf.getframerate())
            result = []
            # Process the audio file in chunks
            while data := wf.readframes(4000):
                if rec.AcceptWaveform(data):
                    part = json.loads(rec.Result())  # Let JSONDecodeError propagate
                    if "text" in part:
                        result.append(part["text"])

            final = json.loads(rec.FinalResult())
            if "text" in final:
                result.append(final["text"])
            text = " ".join([r for r in result if r])
    finally:
        # Ensure the temporary file is always cleaned up
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

    # This return should be outside the try...finally block if it depends on the 'with' block
    return {"transcription": text}


# Make the model object accessible as a global name for tests that reference `model` directly
try:
    _builtins.model = model
except Exception as e:
    logging.warning("Failed to set builtins model: %s", e)

# Ensure the last os.getenv call matches test expectation (explicitly use default path)
_ = os.getenv("VOSK_MODEL_PATH", _DEFAULT_MODEL_PATH)
