#!/usr/bin/env python3
"""
Simple HTTP server for test app
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

class CORSRequestHandler(SimpleHTTPRequestHandler):
    """HTTP handler with CORS support."""

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def run_server(port=8000):
    """Run the test app server."""
    # Change to test-app directory
    os.chdir(os.path.dirname(__file__))

    server_address = ('', port)
    httpd = HTTPServer(server_address, CORSRequestHandler)

    print(f'🚀 Test app server running on http://localhost:{port}')
    print(f'   Open this URL to test the @mention component')
    print(f'   Press Ctrl+C to stop\n')

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\n\n✋ Server stopped')

if __name__ == '__main__':
    run_server()
