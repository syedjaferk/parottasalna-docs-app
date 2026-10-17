import random

from locust import HttpUser, between, task


class ShopUser(HttpUser):
    wait_time = between(0.1, 0.4)

    def on_start(self):
        reply = self.client.post("/login", json={"username": "demo", "password": "secret"})
        self.client.headers["Authorization"] = "Bearer " + reply.json()["token"]

    @task(5)
    def list_products(self):
        self.client.get("/products")

    @task(3)
    def view_product(self):
        product_id = random.randint(1, 3)
        self.client.get(f"/products/{product_id}", name="/products/[id]")   # group all ids in one row

    @task(2)
    def profile(self):
        self.client.get("/profile")

    @task(1)
    def place_order(self):
        self.client.post("/orders", json={"product_id": random.randint(1, 3), "qty": 1})
