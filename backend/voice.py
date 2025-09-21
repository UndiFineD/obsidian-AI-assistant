# backend/voice.py
import os
import wave
import json
import vosk
from fastapi import APIRouter, UploadFile, File

router = APIRouter()

MODEL_PATH = os.getenv("VOSK_MODEL_PATH", "models/vosk-model-small-en-us-0.15")

if not os.path.exists(MODEL_PATH):
    raise RuntimeError(f"Vosk model not found at {MODEL_PATH}. Download from https://alphacephei.com/vosk/models")

model = vosk.Model(MODEL_PATH)

@router.post("/api/voice_transcribe")
async def voice_transcribe(file: UploadFile = File(...)):
    """Transcribe uploaded audio file to text using Vosk (offline)."""
    audio_data = await file.read()

    # Save to temporary wav
    temp_path = "temp_audio.wav"
    with open(temp_path, "wb") as f:
        f.write(audio_data)

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

