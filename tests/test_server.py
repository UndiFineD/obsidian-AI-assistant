#!/usr/bin/env python3
"""
Simple HTTP Server for Obsidian AI Assistant Plugin Testing
Serves the plugin files and provides basic API endpoints for testing
"""

import http.server
import socketserver
import json
import os
import sys
from urllib.parse import urlparse, parse_qs
from pathlib import Path

PORT = 8000

class PluginTestHandler(http.server.SimpleHTTPRequestHandler):
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        print(f"GET request: {path}")
        
        # API endpoints for testing
        if path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "status": "ok", 
                "message": "Obsidian AI Assistant Test Server Running",
                "endpoints": ["/ask", "/reindex", "/web", "/status"]
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        elif path == "/status":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"status": "ok", "backend": "test-mode", "models": ["test-model"]}
            self.wfile.write(json.dumps(response).encode())
            
        elif path.startswith("/plugin"):
            # Serve plugin files
            plugin_path = path.replace("/plugin", "/plugin")
            if os.path.exists(f".{plugin_path}"):
                super().do_GET()
            else:
                self.send_error(404, "Plugin file not found")
        
        else:
            # Default file serving
            super().do_GET()
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        print(f"POST request: {path}")
        
        # Read request data
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            request_data = json.loads(post_data.decode('utf-8')) if post_data else {}
        except:
            request_data = {}
        
        # Mock API responses
        if path == "/ask":
            response = {
                "response": f"Mock AI response to: {request_data.get('prompt', 'No prompt provided')}",
                "model_used": "test-model",
                "processing_time": 0.1
            }
        elif path == "/reindex":
            response = {
                "status": "success",
                "message": "Mock reindexing completed",
                "files_indexed": 42
            }
        elif path == "/web":
            response = {
                "status": "success", 
                "message": "Mock web search completed",
                "results": ["Mock result 1", "Mock result 2"]
            }
        else:
            self.send_error(404, "Endpoint not found")
            return
        
        # Send response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def main():
    # Change to plugin directory to serve files
    os.chdir('plugin')
    
    print("Starting Obsidian AI Assistant Test Server")
    print(f"Serving from: {os.getcwd()}")
    print(f"Server running on: http://localhost:{PORT}")
    print("Test endpoints:")
    print("   GET  / - Server status")
    print("   GET  /status - Backend status")
    print("   POST /ask - Mock AI chat")
    print("   POST /reindex - Mock reindexing")
    print("   POST /web - Mock web search")
    print("\nPlugin files available:")
    
    # List plugin files
    for file in os.listdir('.'):
        if file.endswith(('.js', '.json', '.css')):
            print(f"   http://localhost:{PORT}/{file}")
    
    print("\nTo test: Open Obsidian, enable the plugin, and check console for requests")
    print("Press Ctrl+C to stop the server\n")
    
    # Start server
    with socketserver.TCPServer(("", PORT), PluginTestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")
            sys.exit(0)

if __name__ == "__main__":
    main()