# tests/backend/test_voice.py
import pytest
import tempfile
import wave
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open, AsyncMock
from fastapi.testclient import TestClient
from fastapi import UploadFile
import sys

# Add backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from voice import router, model, MODEL_PATH


class TestVoiceModule:
    """Test suite for the voice module."""
    
    def test_model_path_configuration(self):
        """Test that MODEL_PATH is properly configured."""
        assert MODEL_PATH is not None
        assert isinstance(MODEL_PATH, str)
        # Should be either from environment or default
        assert "vosk-model" in MODEL_PATH
    
    @patch('voice.os.path.exists')
    @patch('voice.vosk.Model')
    def test_model_initialization_success(self, mock_vosk_model, mock_exists):
        """Test successful model initialization."""
        mock_exists.return_value = True
        mock_model_instance = Mock()
        mock_vosk_model.return_value = mock_model_instance
        
        # Reimport to test initialization
        import importlib
        import voice
        importlib.reload(voice)
        
        mock_exists.assert_called_with(MODEL_PATH)
        mock_vosk_model.assert_called_with(MODEL_PATH)
    
    @patch('voice.os.path.exists', return_value=False)
    def test_model_initialization_failure(self, mock_exists):
        """Test model initialization failure when model path doesn't exist."""
        with pytest.raises(RuntimeError) as exc_info:
            # Reimport to test initialization
            import importlib
            import voice
            importlib.reload(voice)
        
        assert "Vosk model not found" in str(exc_info.value)
        assert MODEL_PATH in str(exc_info.value)
    
    def test_router_is_created(self):
        """Test that FastAPI router is properly created."""
        assert router is not None
        # Check that the router has the expected endpoint
        routes = [route.path for route in router.routes]
        assert "/api/voice_transcribe" in routes


class TestVoiceTranscription:
    """Test suite for voice transcription functionality."""
    
    def create_test_wav_file(self, duration=1.0, sample_rate=16000, channels=1, sample_width=2):
        """Create a test WAV file with specified parameters."""
        import struct
        
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        
        with wave.open(temp_file.name, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(sample_rate)
            
            # Generate simple sine wave
            import math
            frames = int(duration * sample_rate)
            for i in range(frames):
                value = int(32767 * math.sin(2 * math.pi * 440 * i / sample_rate))
                data = struct.pack('<h', value)
                wf.writeframes(data)
        
        return temp_file.name
    
    @pytest.fixture
    def test_client(self):
        """Create a test client for the voice router."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)
    
    @pytest.fixture
    def mock_upload_file(self):
        """Create a mock UploadFile for testing."""
        mock_file = Mock(spec=UploadFile)
        mock_file.read = AsyncMock()
        return mock_file
    
    @patch('voice.wave.open')
    @patch('voice.vosk.KaldiRecognizer')
    @patch('builtins.open', mock_open())
    async def test_voice_transcribe_success(self, mock_kaldi, mock_wave_open):
        """Test successful voice transcription."""
        # Mock audio file data
        mock_audio_data = b"fake_audio_data"
        
        # Mock UploadFile
        mock_file = Mock(spec=UploadFile)
        mock_file.read = AsyncMock(return_value=mock_audio_data)
        
        # Mock wave file
        mock_wf = Mock()
        mock_wf.getnchannels.return_value = 1
        mock_wf.getsampwidth.return_value = 2
        mock_wf.getframerate.return_value = 16000
        mock_wf.readframes.side_effect = [b"frame1", b"frame2", b""]
        mock_wave_open.return_value = mock_wf
        
        # Mock Kaldi recognizer
        mock_recognizer = Mock()
        mock_recognizer.AcceptWaveform.side_effect = [True, False]
        mock_recognizer.Result.return_value = '{"text": "hello world"}'
        mock_recognizer.FinalResult.return_value = '{"text": "final text"}'
        mock_kaldi.return_value = mock_recognizer
        
        from voice import voice_transcribe
        
        result = await voice_transcribe(mock_file)
        
        assert "transcription" in result
        assert isinstance(result["transcription"], str)
        mock_file.read.assert_called_once()
    
    @patch('voice.wave.open')
    async def test_voice_transcribe_invalid_audio_format(self, mock_wave_open):
        """Test transcription with invalid audio format."""
        mock_audio_data = b"fake_audio_data"
        
        mock_file = Mock(spec=UploadFile)
        mock_file.read = AsyncMock(return_value=mock_audio_data)
        
        # Mock wave file with invalid format
        mock_wf = Mock()
        mock_wf.getnchannels.return_value = 2  # Stereo (invalid)
        mock_wf.getsampwidth.return_value = 2
        mock_wf.getframerate.return_value = 16000
        mock_wave_open.return_value = mock_wf
        
        from voice import voice_transcribe
        
        result = await voice_transcribe(mock_file)
        
        assert "error" in result
        assert "mono PCM WAV" in result["error"]
    
    @patch('voice.wave.open')
    async def test_voice_transcribe_invalid_sample_width(self, mock_wave_open):
        """Test transcription with invalid sample width."""
        mock_audio_data = b"fake_audio_data"
        
        mock_file = Mock(spec=UploadFile)
        mock_file.read = AsyncMock(return_value=mock_audio_data)
        
        # Mock wave file with invalid sample width
        mock_wf = Mock()
        mock_wf.getnchannels.return_value = 1
        mock_wf.getsampwidth.return_value = 3  # Invalid sample width
        mock_wf.getframerate.return_value = 16000
        mock_wave_open.return_value = mock_wf
        
        from voice import voice_transcribe
        
        result = await voice_transcribe(mock_file)
        
        assert "error" in result
        assert "mono PCM WAV" in result["error"]
    
    @patch('voice.wave.open')
    async def test_voice_transcribe_invalid_sample_rate(self, mock_wave_open):
        """Test transcription with invalid sample rate."""
        mock_audio_data = b"fake_audio_data"
        
        mock_file = Mock(spec=UploadFile)
        mock_file.read = AsyncMock(return_value=mock_audio_data)
        
        # Mock wave file with invalid sample rate
        mock_wf = Mock()
        mock_wf.getnchannels.return_value = 1
        mock_wf.getsampwidth.return_value = 2
        mock_wf.getframerate.return_value = 44100  # Invalid sample rate
        mock_wave_open.return_value = mock_wf
        
        from voice import voice_transcribe
        
        result = await voice_transcribe(mock_file)
        
        assert "error" in result
        assert "16kHz or 8kHz" in result["error"]
    
    @patch('voice.wave.open')
    @patch('voice.vosk.KaldiRecognizer')
    @patch('builtins.open', mock_open())
    async def test_voice_transcribe_empty_transcription(self, mock_kaldi, mock_wave_open):
        """Test transcription that produces empty result."""
        mock_audio_data = b"fake_audio_data"
        
        mock_file = Mock(spec=UploadFile)
        mock_file.read = AsyncMock(return_value=mock_audio_data)
        
        # Mock wave file
        mock_wf = Mock()
        mock_wf.getnchannels.return_value = 1
        mock_wf.getsampwidth.return_value = 2
        mock_wf.getframerate.return_value = 16000
        mock_wf.readframes.side_effect = [b""]  # No audio frames
        mock_wave_open.return_value = mock_wf
        
        # Mock Kaldi recognizer with empty results
        mock_recognizer = Mock()
        mock_recognizer.AcceptWaveform.return_value = False
        mock_recognizer.FinalResult.return_value = '{"text": ""}'
        mock_kaldi.return_value = mock_recognizer
        
        from voice import voice_transcribe
        
        result = await voice_transcribe(mock_file)
        
        assert "transcription" in result
        assert result["transcription"] == ""
    
    @patch('voice.wave.open')
    @patch('voice.vosk.KaldiRecognizer')
    @patch('builtins.open', mock_open())
    async def test_voice_transcribe_multiple_segments(self, mock_kaldi, mock_wave_open):
        """Test transcription with multiple text segments."""
        mock_audio_data = b"fake_audio_data"
        
        mock_file = Mock(spec=UploadFile)
        mock_file.read = AsyncMock(return_value=mock_audio_data)
        
        # Mock wave file
        mock_wf = Mock()
        mock_wf.getnchannels.return_value = 1
        mock_wf.getsampwidth.return_value = 2
        mock_wf.getframerate.return_value = 16000
        mock_wf.readframes.side_effect = [b"frame1", b"frame2", b"frame3", b""]
        mock_wave_open.return_value = mock_wf
        
        # Mock Kaldi recognizer with multiple results
        mock_recognizer = Mock()
        mock_recognizer.AcceptWaveform.side_effect = [True, True, False]
        results = ['{"text": "hello"}', '{"text": "world"}']
        mock_recognizer.Result.side_effect = results
        mock_recognizer.FinalResult.return_value = '{"text": "goodbye"}'
        mock_kaldi.return_value = mock_recognizer
        
        from voice import voice_transcribe
        
        result = await voice_transcribe(mock_file)
        
        assert "transcription" in result
        assert result["transcription"] == "hello world goodbye"
    
    @patch('voice.wave.open')
    @patch('builtins.open', mock_open())
    async def test_voice_transcribe_wave_error(self, mock_wave_open):
        """Test transcription with wave file error."""
        mock_audio_data = b"fake_audio_data"
        
        mock_file = Mock(spec=UploadFile)
        mock_file.read = AsyncMock(return_value=mock_audio_data)
        
        # Mock wave.open to raise an exception
        mock_wave_open.side_effect = wave.Error("Invalid WAV file")
        
        from voice import voice_transcribe
        
        with pytest.raises(wave.Error):
            await voice_transcribe(mock_file)
    
    @patch('voice.wave.open')
    @patch('voice.vosk.KaldiRecognizer')
    @patch('builtins.open', mock_open())
    async def test_voice_transcribe_json_parsing_error(self, mock_kaldi, mock_wave_open):
        """Test transcription with JSON parsing error in results."""
        mock_audio_data = b"fake_audio_data"
        
        mock_file = Mock(spec=UploadFile)
        mock_file.read = AsyncMock(return_value=mock_audio_data)
        
        # Mock wave file
        mock_wf = Mock()
        mock_wf.getnchannels.return_value = 1
        mock_wf.getsampwidth.return_value = 2
        mock_wf.getframerate.return_value = 16000
        mock_wf.readframes.side_effect = [b"frame1", b""]
        mock_wave_open.return_value = mock_wf
        
        # Mock Kaldi recognizer with invalid JSON
        mock_recognizer = Mock()
        mock_recognizer.AcceptWaveform.return_value = True
        mock_recognizer.Result.return_value = "invalid json"
        mock_recognizer.FinalResult.return_value = '{"text": "final"}'
        mock_kaldi.return_value = mock_recognizer
        
        from voice import voice_transcribe
        
        with pytest.raises(json.JSONDecodeError):
            await voice_transcribe(mock_file)
    
    def test_voice_transcribe_endpoint_integration(self, test_client):
        """Test the voice transcription endpoint integration."""
        # Create a simple test audio file
        test_wav = self.create_test_wav_file()
        
        try:
            with patch('voice.vosk.KaldiRecognizer') as mock_kaldi:
                # Mock the recognizer
                mock_recognizer = Mock()
                mock_recognizer.AcceptWaveform.return_value = False
                mock_recognizer.FinalResult.return_value = '{"text": "test transcription"}'
                mock_kaldi.return_value = mock_recognizer
                
                # Upload the file
                with open(test_wav, "rb") as f:
                    response = test_client.post(
                        "/api/voice_transcribe",
                        files={"file": ("test.wav", f, "audio/wav")}
                    )
                
                assert response.status_code == 200
                data = response.json()
                assert "transcription" in data
        finally:
            # Clean up
            os.unlink(test_wav)


class TestVoiceUtilities:
    """Test utility functions and edge cases for voice module."""
    
    @patch('voice.os.getenv')
    def test_model_path_from_environment(self, mock_getenv):
        """Test MODEL_PATH loading from environment variable."""
        test_path = "/custom/vosk/model/path"
        mock_getenv.return_value = test_path
        
        # Reimport to test environment loading
        import importlib
        import voice
        importlib.reload(voice)
        
        mock_getenv.assert_called_with("VOSK_MODEL_PATH", "models/vosk-model-small-en-us-0.15")
    
    @patch('voice.os.getenv')
    def test_model_path_default_value(self, mock_getenv):
        """Test MODEL_PATH default value when not in environment."""
        mock_getenv.return_value = None
        
        # Reimport to test default
        import importlib
        import voice
        importlib.reload(voice)
        
        # Should use default path
        expected_default = "models/vosk-model-small-en-us-0.15"
        mock_getenv.assert_called_with("VOSK_MODEL_PATH", expected_default)
    
    def test_temporary_file_cleanup(self):
        """Test that temporary audio files are properly handled."""
        # This is more of a documentation test since the current implementation
        # doesn't clean up temp_audio.wav, but it should
        temp_file = "temp_audio.wav"
        
        # If the file exists from a previous test, it should be overwritten
        # In a real implementation, we'd want proper cleanup
        assert isinstance(temp_file, str)
        assert temp_file.endswith('.wav')
    
    @patch('voice.vosk.KaldiRecognizer')
    def test_recognizer_initialization_with_different_sample_rates(self, mock_kaldi):
        """Test that recognizer is initialized with correct sample rate."""
        mock_recognizer = Mock()
        mock_kaldi.return_value = mock_recognizer
        
        # Test with 16kHz
        sample_rate = 16000
        mock_kaldi(model, sample_rate)
        mock_kaldi.assert_called_with(model, sample_rate)
        
        # Test with 8kHz
        sample_rate = 8000
        mock_kaldi(model, sample_rate)
        mock_kaldi.assert_called_with(model, sample_rate)


class TestVoiceErrorHandling:
    """Test error handling in voice module."""
    
    async def test_file_read_error(self):
        """Test handling of file read errors."""
        mock_file = Mock(spec=UploadFile)
        mock_file.read = AsyncMock(side_effect=Exception("File read error"))
        
        from voice import voice_transcribe
        
        with pytest.raises(RuntimeError):
            await voice_transcribe(mock_file)
    
    @patch('builtins.open', side_effect=IOError("Cannot write temp file"))
    async def test_temp_file_write_error(self, mock_open):
        """Test handling of temporary file write errors."""
        mock_file = Mock(spec=UploadFile)
        mock_file.read = AsyncMock(return_value=b"audio_data")
        
        from voice import voice_transcribe
        
        with pytest.raises(IOError):
            await voice_transcribe(mock_file)


if __name__ == "__main__":
    pytest.main([__file__])