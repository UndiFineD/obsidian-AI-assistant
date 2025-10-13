#!/usr/bin/env python3
"""Simple backend server starter"""

import uvicorn

from backend.backend import app

if __name__ == "__main__":
    print("Starting Obsidian AI Assistant Backend Server...")
    print("Server will be available at: http://127.0.0.1:8000")
    print("Press Ctrl+C to stop the server")

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
