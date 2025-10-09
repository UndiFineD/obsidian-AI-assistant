import requests

def test_backend_status():
    """Test that the backend server is online and responds to /status."""
    url = "http://localhost:8000/status"
    response = requests.get(url)
    assert response.status_code == 200
    assert "online" in response.text.lower()

def test_ask_endpoint():
    """Test the /ask endpoint with a sample question."""
    url = "http://localhost:8000/ask"
    payload = {"question": "What is Obsidian?", "prefer_fast": True}
    response = requests.post(url, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert isinstance(data["answer"], str)

def test_transcribe_endpoint():
    """Test the /transcribe endpoint with dummy audio data."""
    url = "http://localhost:8000/transcribe"
    payload = {"audio_data": "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=", "format": "wav", "language": "en"}
    response = requests.post(url, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "transcription" in data
