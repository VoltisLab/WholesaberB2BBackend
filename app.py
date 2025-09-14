#!/usr/bin/env python3
"""
Simple Flask-like app for AWS Elastic Beanstalk.
"""

import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/health' or self.path == '/test':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'status': 'success',
                'message': 'AWS Elastic Beanstalk backend is working!',
                'path': self.path,
                'method': 'GET'
            }
            
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('', port), SimpleHandler)
    print(f'Server running on port {port}')
    server.serve_forever()
