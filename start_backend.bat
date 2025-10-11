@echo off
echo Starting Obsidian AI Assistant Backend Server...
echo Server will be available at: http://127.0.0.1:8000
echo Health check: http://127.0.0.1:8000/health
echo API docs: http://127.0.0.1:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

cd /d "%~dp0"
python -m uvicorn backend.backend:app --host 127.0.0.1 --port 8000

pause