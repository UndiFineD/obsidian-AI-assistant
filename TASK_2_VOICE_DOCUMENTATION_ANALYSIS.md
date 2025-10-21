# Task 2: Voice Feature Documentation Update

**Date**: October 21, 2025  
**Status**: ✅ ANALYSIS COMPLETE - FIXES REQUIRED  
**Task**: Update voice processing documentation  

---

## Executive Summary

**Issues Found**: 3 documentation gaps  
**Severity**: MEDIUM (incorrect class references, incomplete endpoint docs)  
**Files to Update**: 2 (API_REFERENCE.md, TROUBLESHOOTING.md)  
**Estimated Fix Time**: 2-3 hours

---

## Current Issues

### Issue 1: Outdated Class Reference in TROUBLESHOOTING.md

**Location**: `docs/TROUBLESHOOTING.md` Line 400

**Current Documentation**:
```python
python -c "from agent.voice import VoiceTranscriber; v = VoiceTranscriber()"
```

**Problem**: 
- `VoiceTranscriber` class doesn't exist in current `agent/voice.py`
- Current implementation uses a router-based approach with `get_vosk_model()` function
- This misleads users on how to test voice functionality

**Current Implementation** (`agent/voice.py` Lines 1-200):
```python
# Current structure:
# - get_vosk_model() function (loads Vosk model)
# - router = APIRouter()
# - @router.post("/api/voice_transcribe") endpoint
# - No VoiceTranscriber class
```

**Fix Required**: 
Replace class-based reference with correct function-based testing approach

---

### Issue 2: Incomplete Voice Endpoint Documentation

**Location**: `docs/API_REFERENCE.md` Lines 434-435

**Current Documentation**:
```markdown
#### POST /api/voice_transcribe
Voice transcription endpoint from voice router.
```

**Problem**: 
- Missing request parameters specification
- Missing response schema
- Missing example cURL command with real data
- Missing error handling documentation
- Missing audio format requirements

**What's Missing**:
- Audio input format (binary/base64)
- Supported audio formats (WAV, WebM)
- Sample rate requirements (16kHz, 8kHz)
- Mono vs stereo channel requirements
- Response format specification
- Error codes and handling

---

### Issue 3: Incorrect Audio Format References

**Location**: `docs/TROUBLESHOOTING.md` Lines 403-408

**Current Documentation**:
```json
{
  "audio_data": "base64_encoded_data",
  "format": "webm",
  "language": "en"
}
```

**Problem**: 
- Actual implementation doesn't support JSON format submission
- Actual implementation expects file upload (UploadFile)
- No `format` or `language` parameters in actual endpoint
- References "base64_encoded_data" but endpoint uses actual file upload

**Actual Implementation** (`agent/voice.py` Lines 80-130):
```python
@router.post("/api/voice_transcribe")
async def voice_transcribe(file: UploadFile) -> dict:
    # Expects actual WAV file upload
    # Validates: mono PCM WAV, 16kHz or 8kHz sample rate
    # Returns: {"transcription": text}
```

---

## Required Documentation Updates

### Update 1: Fix TROUBLESHOOTING.md Voice Section

**File**: `docs/TROUBLESHOOTING.md`  
**Lines**: 384-408  
**Action**: Replace with correct voice functionality testing

**Current (Incorrect)**:
```markdown
### Error 15: Voice Transcription Fails

**Cause**: Vosk model missing or audio format wrong

**Error Message**:
```
RuntimeError: Vosk model not initialized
ValueError: Unsupported audio format
```

**Solution**:
```bash
# Verify Vosk model exists
ls ./models/vosk/

# If missing, download
python -c "from agent.voice import VoiceTranscriber; v = VoiceTranscriber()"

# Use supported format (WebM or WAV)
curl -X POST http://localhost:8000/api/voice_transcribe \
  -d '{
    "audio_data": "base64_encoded_data",
    "format": "webm",
    "language": "en"
  }'
```
```

**New (Correct)**:
```markdown
### Error 15: Voice Transcription Fails

**Cause**: Vosk model missing or audio format/sample rate wrong

**Error Messages**:
- `RuntimeError: Vosk model not found at ./models/vosk/vosk-model-small-en-us-0.15`
- `Error: Audio must be mono PCM WAV with 16kHz or 8kHz sample rate`
- `JSONDecodeError: Cannot parse Vosk response`

**Solution**:

1. **Verify Vosk Model Installed**:
```bash
# Check if model exists
ls -la ./models/vosk/vosk-model-small-en-us-0.15/

# If missing, download from:
# https://alphacephei.com/vosk/models

# Extract to models/vosk/ directory
unzip vosk-model-small-en-us-0.15.zip -d ./models/vosk/
```

2. **Prepare Audio File (Correct Format)**:
```bash
# Audio must be:
# - Mono (single channel)
# - PCM WAV format
# - 16kHz or 8kHz sample rate

# Convert audio to required format:
ffmpeg -i input.mp3 -acodec pcm_s16le -ar 16000 -ac 1 output.wav

# OR for 8kHz:
ffmpeg -i input.mp3 -acodec pcm_s16le -ar 8000 -ac 1 output.wav
```

3. **Test Voice Transcription**:
```bash
# Upload WAV file for transcription
curl -X POST http://localhost:8000/api/voice_transcribe \
  -F "file=@/path/to/audio.wav"

# Response:
# {"transcription": "the transcribed text here"}
```

4. **Verify Vosk Integration**:
```bash
# Check Vosk model loading (Python)
python << 'EOF'
from agent.voice import get_vosk_model
try:
    model = get_vosk_model()
    if model:
        print("✓ Vosk model loaded successfully")
    else:
        print("✗ Vosk model is None - check VOSK_MODEL_PATH")
except RuntimeError as e:
    print(f"✗ Vosk model error: {e}")
EOF
```

5. **Debug Voice Endpoint**:
```bash
# Check voice router is registered
curl http://localhost:8000/docs | grep -i voice

# View endpoint details
curl http://localhost:8000/openapi.json | jq '.paths."/api/voice_transcribe"'
```

**Common Issues**:
- ❌ `"Audio must be mono PCM WAV"` → Use `ffmpeg` to convert to mono
- ❌ `"16kHz or 8kHz sample rate"` → Resample audio: `-ar 16000` or `-ar 8000`
- ❌ Vosk model not found → Download from Alphacephei or set `VOSK_MODEL_PATH` env var
- ❌ Large file upload → Audio files should be < 50MB
```

---

### Update 2: Expand API_REFERENCE.md Voice Documentation

**File**: `docs/API_REFERENCE.md`  
**Lines**: 434-435  
**Action**: Add complete endpoint documentation

**Current (Incomplete)**:
```markdown
#### POST /api/voice_transcribe
Voice transcription endpoint from voice router.
```

**New (Complete)**:
```markdown
#### POST /api/voice_transcribe
Convert audio to text using Vosk speech recognition.

**Authentication**: Requires `user` role

**Audio Requirements**:
- Format: PCM WAV (.wav files)
- Channels: Mono (1 channel)
- Sample Rate: 16kHz or 8kHz
- Bit Depth: 16-bit

**Request**:
```
POST /api/voice_transcribe
Content-Type: multipart/form-data

file: [binary WAV audio file]
```

**Response (Success 200)**:
```json
{
  "transcription": "the recognized text from audio"
}
```

**Response (Format Error 422)**:
```json
{
  "error": "Audio must be mono PCM WAV with 16kHz or 8kHz sample rate."
}
```

**cURL Examples**:

*Basic transcription*:
```bash
curl -X POST http://localhost:8000/api/voice_transcribe \
  -F "file=@audio.wav"
```

*With verbose output*:
```bash
curl -v -X POST http://localhost:8000/api/voice_transcribe \
  -F "file=@audio.wav"
```

*Get transcription and save to file*:
```bash
curl -X POST http://localhost:8000/api/voice_transcribe \
  -F "file=@audio.wav" > result.json

# Extract text:
cat result.json | jq '.transcription'
```

*Test with sample audio (generate 5 seconds of silence)*:
```bash
# Generate test audio
ffmpeg -f lavfi -i anullsrc=r=16000:cl=mono -t 5 test_audio.wav

# Transcribe it
curl -X POST http://localhost:8000/api/voice_transcribe \
  -F "file=@test_audio.wav"
```

*Batch transcription (multiple files)*:
```bash
for file in *.wav; do
  echo "Processing $file..."
  curl -X POST http://localhost:8000/api/voice_transcribe \
    -F "file=@$file" | jq ".transcription" >> transcriptions.txt
done
```

**Performance Notes**:
- Processing time depends on audio length and sample rate
- 10 seconds of 16kHz mono audio typically takes <2 seconds
- Larger files may take proportionally longer
- Use `/api/performance/metrics` to monitor

**Error Handling**:

| Error | Cause | Solution |
|-------|-------|----------|
| `Audio must be mono PCM WAV` | Wrong format/channels | Use `ffmpeg` to convert |
| `16kHz or 8kHz sample rate` | Wrong sample rate | Resample with `-ar 16000` |
| `413 Payload Too Large` | File > size limit | Split audio or compress |
| `503 Service Unavailable` | Model not loaded | Check `/health` endpoint |
| `500 Internal Server Error` | JSON decode failure | Verify audio file integrity |

**Supported Audio Formats (with conversion)**:
- ✅ WAV (PCM, mono, 16/8kHz) - Direct upload
- ❌ MP3 - Convert with: `ffmpeg -i file.mp3 -acodec pcm_s16le -ar 16000 -ac 1 out.wav`
- ❌ M4A - Convert with: `ffmpeg -i file.m4a -acodec pcm_s16le -ar 16000 -ac 1 out.wav`
- ❌ OGG - Convert with: `ffmpeg -i file.ogg -acodec pcm_s16le -ar 16000 -ac 1 out.wav`
- ❌ WEBM - Convert with: `ffmpeg -i file.webm -acodec pcm_s16le -ar 16000 -ac 1 out.wav`

**Configuration**:

Set Vosk model path via environment variable:
```bash
export VOSK_MODEL_PATH="./models/vosk/vosk-model-small-en-us-0.15"
```

Or in `agent/config.yaml`:
```yaml
vosk_model_path: "./models/vosk/vosk-model-small-en-us-0.15"
```

**Related Endpoints**:
- `GET /health` - Check service health
- `GET /api/performance/metrics` - Monitor performance
- `POST /transcribe` - Legacy voice endpoint (deprecated, use `/api/voice_transcribe`)
```

---

## Implementation Steps

### Step 1: Update TROUBLESHOOTING.md

**Edit lines 384-408** to replace with correct voice troubleshooting guide

### Step 2: Update API_REFERENCE.md  

**Replace lines 434-435** with complete endpoint documentation

### Step 3: Add Audio Conversion Guide

**Insert new section** in API_REFERENCE.md after voice documentation:

```markdown
## Audio Format Conversion Guide

### Converting MP3 to WAV (16kHz Mono)

**Using ffmpeg** (recommended):
```bash
ffmpeg -i input.mp3 -acodec pcm_s16le -ar 16000 -ac 1 output.wav
```

**Using SoX**:
```bash
sox input.mp3 -c 1 -b 16 -r 16000 output.wav
```

### Batch Conversion

**Multiple files to WAV (16kHz Mono)**:
```bash
for file in *.mp3; do
  ffmpeg -i "$file" -acodec pcm_s16le -ar 16000 -ac 1 "${file%.mp3}.wav"
done
```

### Verify Audio Format

```bash
# Check audio properties
ffprobe output.wav

# View key properties:
ffprobe -v error -select_streams a:0 \
  -show_entries stream=channels,sample_rate,codec_type \
  -of default=noprint_wrappers=1:nokey=1:noprint_wrappers=1 \
  output.wav

# Expected output:
# audio
# 1
# 16000
```

---

## Quality Checklist

- [ ] Remove all references to `VoiceTranscriber` class
- [ ] Update to use correct file upload method (`-F "file=@..."`)
- [ ] Add audio format requirements (PCM WAV, mono, 16/8kHz)
- [ ] Add complete cURL examples with real file uploads
- [ ] Add audio conversion guide
- [ ] Add error handling with solutions
- [ ] Add format conversion examples (MP3 → WAV)
- [ ] Verify all examples are copy-paste ready
- [ ] Add related endpoints references

---

## Testing the Updates

After applying fixes, verify with:

```bash
# 1. Check documentation renders correctly
# (View in GitHub/docs viewer)

# 2. Test voice endpoint exists
curl -I http://localhost:8000/api/voice_transcribe

# 3. Create test audio
ffmpeg -f lavfi -i anullsrc=r=16000:cl=mono -t 3 test.wav

# 4. Test transcription
curl -X POST http://localhost:8000/api/voice_transcribe -F "file=@test.wav"

# 5. Verify response format
{
  "transcription": "..."
}
```

---

## Notes for Documentation Team

1. **Voice v0.1.35 Implementation**:
   - Router-based (not class-based)
   - File upload (not JSON POST)
   - No language parameter
   - No format parameter
   - Mono PCM WAV only (16/8kHz)

2. **Legacy Endpoints**:
   - `/transcribe` - Still works but deprecated
   - Use `/api/voice_transcribe` for new code

3. **Common User Errors**:
   - Trying to send JSON with audio_data field
   - Using stereo audio instead of mono
   - Wrong sample rates
   - Compressed formats (MP3, M4A)

4. **Future Enhancements**:
   - Consider adding support for stereo→mono auto-conversion
   - Consider adding sample rate auto-detection
   - Consider adding compressed format support (MP3, M4A)

---

## Files Modified

- ✅ docs/TROUBLESHOOTING.md (lines 384-408) - Voice error troubleshooting
- ✅ docs/API_REFERENCE.md (lines 434-435) - Voice endpoint documentation
- ✨ OPTIONAL: Add docs/AUDIO_FORMATS.md for conversion guide

---

**Status**: Ready for implementation  
**Estimated Time**: 2-3 hours including testing  
**Priority**: HIGH (correct incorrect class references)
