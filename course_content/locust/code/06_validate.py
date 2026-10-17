from locust import HttpUser, between, task


class CheckingUser(HttpUser):
    wait_time = between(0.1, 0.3)

    @task
    def login_has_token(self):
        with self.client.post("/login", json={"username": "demo", "password": "secret"}, catch_response=True) as response:
            if "token" not in response.json():
                response.failure("login reply has no token")

    @task
    def missing_product_is_expected(self):
        # a 404 is normally a failure, but here it is the correct answer
        with self.client.get("/products/99", name="/products/[missing]", catch_response=True) as response:
            if response.status_code == 404:
                response.success()

    @task
    def slow_page(self):
        with self.client.get("/slow", catch_response=True) as response:
            if response.elapsed.total_seconds() > 0.25:
                response.failure(f"too slow: {response.elapsed.total_seconds():.2f}s")

    @task
    def flaky_page(self):
        self.client.get("/flaky")           # the server fails every 4th call with a 500
