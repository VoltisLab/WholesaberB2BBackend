#!/usr/bin/env python3
"""
Simple test application to verify AWS deployment is working.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import os

class TestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<h1>Backend is working!</h1><p>This is a test response from AWS Elastic Beanstalk.</p>')
    
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"status": "success", "message": "Backend is working!"}')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), TestHandler)
    print(f'Test server running on port {port}')
    server.serve_forever()
