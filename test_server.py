#!/usr/bin/env python3
"""
Simple HTTP Server for Obsidian AI Assistant Testing (no Node.js required)
- Serves plugin files from the ./plugin directory
- Exposes minimal mock API endpoints used by the plugin: /, /status, /ask, /reindex, /web

Usage:
  python test_server.py
Then open http://localhost:8000 in your browser or point the plugin to http://localhost:8000
"""

import http.server
import socketserver
import json
import os
import sys
from urllib.parse import urlparse

PORT = 8000
PLUGIN_DIR = os.path.join(os.path.dirname(__file__), "plugin")

class PluginTestHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path: str):
        # Always serve files relative to the plugin directory for static assets
        # API endpoints are handled in do_GET/POST and won't use this
        path = super().translate_path(path)
        # Map to plugin directory by replacing current cwd path prefix
        try:
            cwd = os.getcwd()
            if path.startswith(cwd):
                suffix = path[len(cwd):].lstrip("/\\")
                return os.path.join(PLUGIN_DIR, suffix)
        except Exception:
            pass
        return path

    def end_headers(self):
        # CORS headers for convenience
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            payload = {
                "status": "ok",
                "message": "Obsidian AI Assistant Test Server Running",
                "endpoints": ["/ask", "/reindex", "/web", "/status"],
            }
            self.wfile.write(json.dumps(payload, indent=2).encode("utf-8"))
            return
        if path == "/status":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "backend": "test-mode", "models": ["test-model"]}).encode("utf-8"))
            return
        # Otherwise serve static from plugin directory
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get('Content-Length', '0') or 0)
        raw = self.rfile.read(length) if length else b""
        try:
            data = json.loads(raw.decode('utf-8')) if raw else {}
        except Exception:
            data = {}
        if path == "/ask":
            resp = {
                "response": f"Mock AI response to: {data.get('prompt', 'No prompt provided')}",
                "model_used": "test-model",
                "processing_time": 0.1,
            }
        elif path == "/reindex":
            resp = {
                "status": "success",
                "message": "Mock reindexing completed",
                "files_indexed": 42,
            }
        elif path == "/web":
            resp = {
                "status": "success",
                "message": "Mock web search completed",
                "results": ["Mock result 1", "Mock result 2"],
            }
        else:
            self.send_error(404, "Endpoint not found")
            return
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(resp, indent=2).encode('utf-8'))


def main():
    # Ensure plugin dir exists
    if not os.path.isdir(PLUGIN_DIR):
        print(f"Plugin directory not found: {PLUGIN_DIR}")
        sys.exit(1)
    os.chdir(PLUGIN_DIR)
    print("Starting Obsidian AI Assistant Test Server (Python only)")
    print(f"Serving plugin from: {PLUGIN_DIR}")
    print(f"Open: http://localhost:{PORT}")
    print("Endpoints: GET /, GET /status, POST /ask, POST /reindex, POST /web")
    with socketserver.TCPServer(("", PORT), PluginTestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")
            sys.exit(0)


if __name__ == "__main__":
    main()
