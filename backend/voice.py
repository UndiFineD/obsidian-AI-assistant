# backend/voice.py

import os
import tempfile
from fastapi import APIRouter, UploadFile, File
from .utils import safe_call


# Robust voice transcription endpoint

_DEFAULT_MODEL_PATH = "models/vosk-model-small-en-us-0.15"
def get_vosk_model():
    import vosk
    model_path = os.getenv("VOSK_MODEL_PATH", _DEFAULT_MODEL_PATH)
    def do_get_model():
        if not os.path.exists(model_path):
            if model_path == _DEFAULT_MODEL_PATH:
                raise RuntimeError(
                    f"Vosk model not found at {model_path}. Download from https://alphacephei.com/vosk/models"
                )
            print(f"Warning: Vosk model path from environment does not exist: {model_path}. Proceeding without model.")
            return None
        return vosk.Model(model_path)
    return safe_call(do_get_model, error_msg=f"Failed to load Vosk model from {model_path}", default=None)

router = APIRouter()

@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    import wave
    import json
    import vosk
    model = get_vosk_model()
    if model is None:
        return {"error": "Voice transcription not available - Vosk model not loaded"}
    async def do_read_audio():
        return await file.read()
    audio_data = await do_read_audio()

    # Save to secure temporary wav
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
        temp_path = temp_wav.name
        temp_wav.write(audio_data)

    try:
        wf = wave.open(temp_path, "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() not in [16000, 8000]:
            return {"error": "Audio must be mono PCM WAV with 16kHz or 8kHz sample rate."}
        rec = vosk.KaldiRecognizer(model, wf.getframerate())
        result = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                part = json.loads(rec.Result())
                if "text" in part:
                    result.append(part["text"])
        final = json.loads(rec.FinalResult())
        if "text" in final:
            result.append(final["text"])
        text = " ".join([r for r in result if r])
        return {"transcription": text}
    except Exception as e:
        print(f"Voice transcription error: {e}")
        return {"error": str(e)}
    finally:
        try:
            os.remove(temp_path)
        except Exception:
            pass

