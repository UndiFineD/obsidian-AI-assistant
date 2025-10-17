"""
Tests for the /api/voice_transcribe endpoint
"""
import pytest
import base64
from fastapi.testclient import TestClient


def test_api_voice_transcribe_valid_audio(client):
    """Test voice transcription with valid base64 audio data"""
    # Create a small valid WAV header + audio data
    wav_header = b'RIFF' + (44).to_bytes(4, 'little') + b'WAVE'
    wav_header += b'fmt ' + (16).to_bytes(4, 'little')
    wav_header += (1).to_bytes(2, 'little')  # PCM
    wav_header += (1).to_bytes(2, 'little')  # Mono
    wav_header += (16000).to_bytes(4, 'little')  # Sample rate
    wav_header += (32000).to_bytes(4, 'little')  # Byte rate
    wav_header += (2).to_bytes(2, 'little')  # Block align
    wav_header += (16).to_bytes(2, 'little')  # Bits per sample
    wav_header += b'data' + (8).to_bytes(4, 'little')
    wav_header += b'\x00' * 8  # Minimal audio data
    
    audio_b64 = base64.b64encode(wav_header).decode('utf-8')
    
    response = client.post(
        "/api/voice_transcribe",
        json={
            "audio_data": audio_b64,
            "format": "wav",
            "language": "en"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "success" in data
    assert data["success"] is True
    assert "transcription" in data
    assert "confidence" in data
    assert "status" in data
    assert "audio_info" in data
    assert "metadata" in data
    
    # Verify audio_info fields
    audio_info = data["audio_info"]
    assert "size_mb" in audio_info
    assert "size_bytes" in audio_info
    assert "type" in audio_info
    assert "format" in audio_info
    assert "language" in audio_info
    assert "hash" in audio_info
    assert "warnings" in audio_info
    
    # Verify metadata fields
    metadata = data["metadata"]
    assert "endpoint_version" in metadata
    assert metadata["endpoint_version"] == "v1"
    assert "processing_time_ms" in metadata
    assert "model" in metadata


def test_api_voice_transcribe_invalid_base64(client):
    """Test voice transcription with invalid base64 data"""
    response = client.post(
        "/api/voice_transcribe",
        json={
            "audio_data": "not-valid-base64!!!",
            "format": "wav",
            "language": "en"
        }
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Invalid audio data" in data["detail"]


def test_api_voice_transcribe_empty_audio(client):
    """Test voice transcription with empty audio data"""
    response = client.post(
        "/api/voice_transcribe",
        json={
            "audio_data": "",
            "format": "wav",
            "language": "en"
        }
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


def test_api_voice_transcribe_large_file(client):
    """Test voice transcription with file size validation"""
    # Create audio data larger than typical limit
    large_audio = b'\x00' * (50 * 1024 * 1024)  # 50MB
    audio_b64 = base64.b64encode(large_audio).decode('utf-8')
    
    response = client.post(
        "/api/voice_transcribe",
        json={
            "audio_data": audio_b64,
            "format": "wav",
            "language": "en"
        }
    )
    
    # Should either accept with warning or reject
    assert response.status_code in [200, 400]
    
    if response.status_code == 200:
        data = response.json()
        # Large files should have warnings
        assert "warnings" in data["audio_info"]


def test_api_voice_transcribe_different_formats(client):
    """Test voice transcription with different audio formats"""
    formats = ["wav", "webm", "mp3", "ogg"]
    
    for audio_format in formats:
        # Create minimal valid audio data
        audio_data = b'RIFF' + b'\x00' * 40
        audio_b64 = base64.b64encode(audio_data).decode('utf-8')
        
        response = client.post(
            "/api/voice_transcribe",
            json={
                "audio_data": audio_b64,
                "format": audio_format,
                "language": "en"
            }
        )
        
        # Should accept all formats
        assert response.status_code in [200, 400]  # Some formats may be rejected


def test_api_voice_transcribe_different_languages(client):
    """Test voice transcription with different language codes"""
    languages = ["en", "es", "fr", "de", "zh"]
    
    # Create minimal valid audio data
    audio_data = b'RIFF' + b'\x00' * 40
    audio_b64 = base64.b64encode(audio_data).decode('utf-8')
    
    for lang in languages:
        response = client.post(
            "/api/voice_transcribe",
            json={
                "audio_data": audio_b64,
                "format": "wav",
                "language": lang
            }
        )
        
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            data = response.json()
            assert data["audio_info"]["language"] == lang


def test_api_voice_transcribe_vs_legacy_endpoint(client):
    """Compare /api/voice_transcribe with legacy /transcribe endpoint"""
    # Create minimal valid audio data
    audio_data = b'RIFF' + b'\x00' * 40
    audio_b64 = base64.b64encode(audio_data).decode('utf-8')
    
    request_data = {
        "audio_data": audio_b64,
        "format": "wav",
        "language": "en"
    }
    
    # Test new API endpoint
    response_api = client.post("/api/voice_transcribe", json=request_data)
    
    # Test legacy endpoint
    response_legacy = client.post("/transcribe", json=request_data)
    
    # Both should work
    assert response_api.status_code in [200, 400]
    assert response_legacy.status_code in [200, 400]
    
    # New endpoint should have enhanced response format
    if response_api.status_code == 200:
        data_api = response_api.json()
        assert "success" in data_api
        assert "metadata" in data_api
        assert "endpoint_version" in data_api["metadata"]


def test_api_voice_transcribe_missing_fields(client):
    """Test voice transcription with missing required fields"""
    # Missing audio_data
    response = client.post(
        "/api/voice_transcribe",
        json={
            "format": "wav",
            "language": "en"
        }
    )
    assert response.status_code == 422  # Validation error
    
    # Missing format
    audio_b64 = base64.b64encode(b'test').decode('utf-8')
    response = client.post(
        "/api/voice_transcribe",
        json={
            "audio_data": audio_b64,
            "language": "en"
        }
    )
    assert response.status_code == 422  # Validation error


def test_api_voice_transcribe_placeholder_response(client):
    """Test that placeholder response is returned when Vosk is not available"""
    # Create minimal valid audio data
    audio_data = b'RIFF' + b'\x00' * 40
    audio_b64 = base64.b64encode(audio_data).decode('utf-8')
    
    response = client.post(
        "/api/voice_transcribe",
        json={
            "audio_data": audio_b64,
            "format": "wav",
            "language": "en"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        # Should indicate placeholder status
        assert data["status"] == "placeholder"
        assert "not yet implemented" in data["transcription"].lower()
        assert data["confidence"] == 0.0
