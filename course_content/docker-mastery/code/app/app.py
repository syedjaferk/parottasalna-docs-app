"""A tiny web app: counts visits in memory and prints a greeting."""
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

GREETING = os.environ.get("GREETING", "Hello")
visits = 0


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global visits
        visits += 1
        body = f"{GREETING} from Docker! visit {visits}\n".encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
