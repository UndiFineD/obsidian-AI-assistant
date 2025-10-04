import os
import sys
import json
import wave
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient

# Add project root to path
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)

# Import after path setup
from backend.voice import router  # noqa: E402


class TestVoiceProcessing(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path("test_audio")
        self.test_dir.mkdir(exist_ok=True)
        self.client = TestClient(router)

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists("temp_audio.wav"):
            os.remove("temp_audio.wav")

    def create_test_wav(
        self,
        filename: str,
        sample_rate: int = 16000
    ) -> bytes:
        """Create a test WAV file."""
        filepath = self.test_dir / filename
        with wave.open(str(filepath), "wb") as wf:
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(sample_rate)
            wf.writeframes(b"\x00" * sample_rate)  # 1 second of silence
        
        with open(filepath, "rb") as f:
            return f.read()

    @patch("backend.voice.vosk.Model")
    @patch("backend.voice.vosk.KaldiRecognizer")
    async def test_transcribe_valid_audio(self, mock_recognizer, mock_model):
        """Test transcription of valid audio file."""
        # Prepare mock response
        mock_instance = MagicMock()
        mock_instance.Result.return_value = json.dumps({"text": "test"})
        mock_instance.FinalResult.return_value = json.dumps({"text": "final"})
        mock_instance.AcceptWaveform.return_value = True
        mock_recognizer.return_value = mock_instance

        # Create test audio file
        test_audio = self.create_test_wav("valid.wav")
        mock_file = AsyncMock()
        mock_file.read = AsyncMock(return_value=test_audio)
        
        response = await self.client.post(
            "/api/voice_transcribe",
            files={"file": ("test.wav", test_audio, "audio/wav")}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("transcription", data)
        self.assertEqual(data["transcription"], "test final")

    @patch("backend.voice.vosk.Model")
    @patch("backend.voice.vosk.KaldiRecognizer")
    async def test_transcribe_empty_audio(self, mock_recognizer, mock_model):
        """Test transcription of empty audio file."""
        # Create empty audio file
        test_audio = self.create_test_wav("empty.wav")
        mock_file = AsyncMock()
        mock_file.read = AsyncMock(return_value=test_audio)

        # Mock empty response
        mock_instance = MagicMock()
        mock_instance.Result.return_value = json.dumps({"text": ""})
        mock_instance.FinalResult.return_value = json.dumps({"text": ""})
        mock_instance.AcceptWaveform.return_value = True
        mock_recognizer.return_value = mock_instance

        response = await self.client.post(
            "/api/voice_transcribe",
            files={"file": ("empty.wav", test_audio, "audio/wav")}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("transcription", data)
        self.assertEqual(data["transcription"], "")

    async def test_transcribe_invalid_format(self):
        """Test handling of invalid audio format."""
        # Create non-WAV file
        test_data = b"Not a WAV file"
        
        response = await self.client.post(
            "/api/voice_transcribe",
            files={"file": ("test.txt", test_data, "text/plain")}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("error", data)

    async def test_transcribe_wrong_sample_rate(self):
        """Test handling of audio with wrong sample rate."""
        # Create WAV with unsupported sample rate
        test_audio = self.create_test_wav("wrong_rate.wav", sample_rate=44100)
        
        response = await self.client.post(
            "/api/voice_transcribe",
            files={"file": ("test.wav", test_audio, "audio/wav")}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("error", data)
        self.assertIn("16kHz or 8kHz", data["error"])


if __name__ == '__main__':
    unittest.main()
