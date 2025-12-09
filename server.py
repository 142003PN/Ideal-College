#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import io
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import UnixStreamServer
from mimetypes import guess_type
import django
from django.core.handlers.wsgi import WSGIHandler

# -------------------------------
# Django setup
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project.settings')
django.setup()
application = WSGIHandler()

# -------------------------------
# HTTP Request Handler
# -------------------------------
class RequestHandler(BaseHTTPRequestHandler):

    def _set_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors()
        self.end_headers()

    def do_GET(self):
        # ---------------------------------
        # ISPmanager health check (HTTP/1.0, no Host)
        # ---------------------------------
        if self.request_version == "HTTP/1.0" and "Host" not in self.headers:
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
            return

        # ---------------------------------
        # Serve static files
        # ---------------------------------
        if self.path.startswith('/static/'):
            static_path = os.path.join(BASE_DIR, self.path.lstrip('/'))
            if os.path.isfile(static_path):
                mime = guess_type(static_path)[0] or "application/octet-stream"
                self.send_response(200)
                self.send_header("Content-Type", mime)
                self._set_cors()
                self.end_headers()
                with open(static_path, 'rb') as f:
                    self.wfile.write(f.read())
                return

        # ---------------------------------
        # All other requests → Django WSGI
        # ---------------------------------
        self._handle_wsgi()

    def do_POST(self):
        self._handle_wsgi()

    def _handle_wsgi(self):
        path = self.path.split('?', 1)[0]
        if not path.startswith("/"):
            path = "/" + path

        env = {
            'REQUEST_METHOD': self.command,
            'PATH_INFO': path,
            'QUERY_STRING': self.path.split('?', 1)[1] if '?' in self.path else '',
            'CONTENT_TYPE': self.headers.get('Content-Type', ''),
            'CONTENT_LENGTH': self.headers.get('Content-Length', '0'),
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': os.environ.get('PORT', '80'),
            'SERVER_PROTOCOL': self.protocol_version,
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'http',
            'wsgi.input': self.rfile,
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
            'SCRIPT_NAME': '',
        }

        # Convert headers to WSGI format
        for key, value in self.headers.items():
            env[f"HTTP_{key.upper().replace('-', '_')}"] = value

        output = io.BytesIO()

        def start_response(status, headers, exc_info=None):
            self.send_response(int(status.split()[0]))
            headers.append(("Access-Control-Allow-Origin", "*"))
            headers.append(("Access-Control-Allow-Methods", "GET, POST, OPTIONS"))
            headers.append(("Access-Control-Allow-Headers", "*"))
            for h, v in headers:
                self.send_header(h, v)
            self.end_headers()
            return output.write

        for data in application(env, start_response):
            output.write(data)

        self.wfile.write(output.getvalue())

# -------------------------------
# Unix socket server
# -------------------------------
class UnixSocketHTTPServer(UnixStreamServer):
    def get_request(self):
        req, client_addr = super().get_request()
        # Unix sockets don't have real IP → prevent IndexError
        return (req, ("local", 0))

# -------------------------------
# Custom HTTPServer for HTTP/1.0 no-Host
# -------------------------------
class ISPHTTPServer(HTTPServer):
    def verify_request(self, request, client_address):
        return True  # accept all requests (including HTTP/1.0 without Host)

# -------------------------------
# Run on TCP port
# -------------------------------
def run_on_port():
    host = os.environ.get('INSTANCE_HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', '8000'))
    server = ISPHTTPServer((host, port), RequestHandler)
    print(f"Listening http://{host}:{port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped by user")

# -------------------------------
# Run on Unix socket
# -------------------------------
def run_on_socket():
    socket_path = os.environ.get('SOCKET', '/tmp/http.sock')
    if os.path.exists(socket_path):
        os.unlink(socket_path)
    server = UnixSocketHTTPServer(socket_path, RequestHandler)
    os.chmod(socket_path, 0o660)
    print(f"Listening on unix://{socket_path}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped by user")

# -------------------------------
# Entry point
# -------------------------------
if 'SOCKET' in os.environ:
    run_on_socket()
else:
    run_on_port()
