from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from agent.backend import app

# Skip all tests in this module if plugin is not deployed
pytestmark = pytest.mark.skipif(
    not Path(".obsidian/plugins/obsidian-ai-agent").exists(),
    reason="Plugin not deployed to .obsidian/plugins/obsidian-ai-agent. "
    "These tests require a deployed Obsidian plugin. "
    "Run './setup-plugin.ps1' to deploy to your Obsidian vault.",
)

# Create test client
client = TestClient(app)


def test_plugin_main_exists():
    """Test that the plugin main.js file exists."""
    plugin_main = Path(".obsidian/plugins/obsidian-ai-agent/main.js")
    assert plugin_main.exists(), "main.js should exist in the plugin directory"


def test_agent_status():
    """Test that the backend server responds to /status endpoint."""
    with patch("agent.agent.init_services") as mock_init:
        mock_init.return_value = None
        response = client.get("/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


def test_ask_endpoint():
    """Test the /ask endpoint with a sample question."""
    with patch("agent.agent.model_manager") as mock_mm, patch(
        "agent.agent.init_services"
    ) as mock_init:
        # Mock the services to avoid initialization
        mock_init.return_value = None
        mock_mm.generate.return_value = "Obsidian is a note-taking application."
        mock_mm.__bool__ = lambda self: True

        payload = {"question": "What is Obsidian?", "prefer_fast": True}
        response = client.post("/ask", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert isinstance(data["answer"], str)


def test_transcribe_endpoint():
    """Test the /transcribe endpoint with dummy audio data."""
    payload = {
        "audio_data": "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=",
        "format": "wav",
        "language": "en",
    }
    response = client.post("/transcribe", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "transcription" in data
    # Should return the placeholder response
    assert "Server-side speech recognition not yet implemented" in data["transcription"]
