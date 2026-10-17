"""A small practice web shop to load test. Standard library only.  Run:  python shop_server.py  (port 8765)"""
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PRODUCTS = {1: {"id": 1, "name": "Laptop", "price": 1000}, 2: {"id": 2, "name": "Phone", "price": 500},
            3: {"id": 3, "name": "Headphones", "price": 100}}
lock = threading.Lock()
state = {"orders": 0, "flaky": 0}


class Shop(BaseHTTPRequestHandler):
    def reply(self, status, body):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length) or b"{}")

    def do_GET(self):
        if self.path == "/":
            self.reply(200, {"message": "Welcome to the shop"})
        elif self.path == "/products":
            self.reply(200, list(PRODUCTS.values()))
        elif self.path.startswith("/products/"):
            product = PRODUCTS.get(int(self.path.rsplit("/", 1)[1]))
            self.reply(200, product) if product else self.reply(404, {"error": "no such product"})
        elif self.path == "/profile":
            if self.headers.get("Authorization") == "Bearer abc123":
                self.reply(200, {"user": "demo"})
            else:
                self.reply(401, {"error": "login first"})
        elif self.path == "/slow":
            time.sleep(0.3)
            self.reply(200, {"message": "that took a while"})
        elif self.path == "/flaky":
            with lock:
                state["flaky"] += 1
                bad = state["flaky"] % 4 == 0
            self.reply(500, {"error": "boom"}) if bad else self.reply(200, {"message": "ok"})
        else:
            self.reply(404, {"error": "not found"})

    def do_POST(self):
        body = self.read_json()
        if self.path == "/login":
            if body.get("username") == "demo" and body.get("password") == "secret":
                self.reply(200, {"token": "abc123"})
            else:
                self.reply(401, {"error": "bad credentials"})
        elif self.path == "/orders":
            with lock:
                state["orders"] += 1
                order_id = state["orders"]
            self.reply(201, {"order_id": order_id, "product_id": body.get("product_id"), "qty": body.get("qty", 1)})
        else:
            self.reply(404, {"error": "not found"})

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8765), Shop).serve_forever()
