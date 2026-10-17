"""Diagrams for the Load Testing with Locust course. Run:  python course_content/locust/diagrams/make_diagrams.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "docs"))
from diagram_kit import D  # noqa: E402


def new(name, w, h, title, caption):
    return D(name, w, h, title, caption, HERE)


def load_idea():
    d = new("load-idea", 760, 250, "What a load test does",
            "Locust runs many simulated users against your service while you watch response time, requests per second and failures.")
    d.box(20, 70, 190, 100, [("Locust", "bold"), ("simulated users", "small"), ("u1 u2 u3 ... u500", "code")], "blue")
    d.box(320, 70, 190, 100, [("Your service", "bold"), ("web app + database", "small")], "amber")
    d.box(600, 40, 140, 160, [("You watch", "bold"), ("response time", "small"), ("requests/second", "small"), ("failures", "small")], "green")
    d.arrow([(212, 120), (318, 120)], kind="blue", label="requests", lx=265, ly=102)
    d.arrow([(512, 120), (598, 120)], kind="green", label="numbers", lx=555, ly=102)
    return d.render()


def user_loop():
    d = new("user-loop", 760, 250, "What one simulated user does",
            "A user picks a task, runs it, waits for the wait time, then picks the next task. Tasks with a bigger weight are picked more often.")
    d.box(20, 40, 150, 70, [("pick a task", "bold"), ("by weight", "small")], "blue")
    d.box(240, 40, 150, 70, [("run it", "bold"), ("e.g. GET /products", "small")], "green")
    d.box(460, 40, 150, 70, [("wait", "bold"), ("between(1, 3)", "code")], "amber")
    d.arrow([(172, 75), (238, 75)], kind="blue")
    d.arrow([(392, 75), (458, 75)], kind="blue")
    d.arrow([(535, 112), (535, 150), (95, 150), (95, 112)], kind="blue", dashed=True)
    d.text(315, 140, "repeat until the test stops", "small")
    d.box(20, 180, 720, 50, [("@task(3) browse   ·   @task(1) buy      →      browse about 3 times for every buy", "code")], "ghost")
    return d.render()


def wait_types():
    d = new("wait-types", 760, 260, "Three kinds of wait time",
            "constant waits a fixed time after each task, between waits a random time, and constant_pacing starts a task at a fixed rhythm.")
    rows = [("constant(1)", "task, then wait 1 s", [(60, 60, "blue"), (120, 90, "box"), (210, 60, "blue"), (270, 90, "box"), (360, 60, "blue")]),
            ("between(0.5, 1.5)", "task, then wait 0.5 to 1.5 s", [(60, 60, "blue"), (120, 50, "box"), (170, 60, "blue"), (230, 120, "box"), (350, 60, "blue")]),
            ("constant_pacing(1)", "one task STARTS every 1 s", [(60, 60, "blue"), (120, 60, "box"), (180, 60, "blue"), (240, 60, "box"), (300, 60, "blue")])]
    for i, (a, b, segs) in enumerate(rows):
        y = 20 + i * 76
        d.text(480, y + 12, a, "code", anchor="start")
        d.text(480, y + 36, b, "small", anchor="start")
        for x, w, k in segs:
            d.rect(x - 40 + 0, y + 10, w, 30, k)
    d.text(220, 245, "blue = the task running, grey = waiting", "small")
    return d.render()


def lifecycle():
    d = new("locust-lifecycle", 760, 250, "Test and user lifecycle hooks",
            "test_start runs once before the users. Each user runs on_start, then its tasks, then on_stop. test_stop runs once at the end.")
    items = [("test_start", "once", "amber"), ("on_start", "per user", "blue"), ("tasks repeat", "per user", "green"), ("on_stop", "per user", "blue"), ("test_stop", "once", "amber")]
    for i, (a, b, k) in enumerate(items):
        x = 15 + i * 148
        d.box(x, 60, 128, 70, [(a, "bold"), (b, "small")], k)
        if i:
            d.arrow([(x - 18, 95), (x - 1, 95)], kind="blue")
    d.text(380, 175, "log in in on_start, clean up in on_stop, open and close reports in test_start / test_stop", "small")
    return d.render()


def http_flow():
    d = new("locust-http", 760, 250, "HttpUser talks to your service",
            "Each HttpUser has a client. Requests are recorded by name, so you can group many URLs into one row of the results.")
    d.box(20, 60, 200, 120, [("HttpUser", "bold"), ("self.client.get(...)", "code"), ("self.client.post(...)", "code")], "blue")
    d.box(320, 60, 170, 120, [("Your service", "bold"), ("/products", "code"), ("/login", "code")], "amber")
    d.box(580, 60, 160, 120, [("Stats row", "bold"), ("#reqs · fails", "small"), ("avg · p95 · req/s", "small")], "green")
    d.arrow([(222, 105), (318, 105)], kind="blue", label="GET/POST", lx=270, ly=88)
    d.arrow([(318, 145), (222, 145)], kind="green", dashed=True)
    d.arrow([(492, 120), (578, 120)], kind="green", label="recorded", lx=535, ly=102)
    d.text(380, 215, "name=\"/products/[id]\" folds /products/1, /products/2 ... into one row", "small")
    return d.render()


def validate():
    d = new("locust-validate", 760, 250, "Deciding pass or fail yourself",
            "With catch_response you look at the reply and call success() or failure(). Without it, Locust fails only on error status codes.")
    d.box(20, 80, 150, 60, [("reply arrives", "bold")], "blue")
    d.box(250, 80, 200, 60, [("check it", "bold"), ("status · body · time", "small")], "amber")
    d.box(550, 20, 190, 56, [("response.success()", "code")], "green")
    d.box(550, 140, 190, 56, [("response.failure(why)", "code")], "red")
    d.arrow([(172, 110), (248, 110)], kind="blue")
    d.arrow([(452, 100), (548, 50)], kind="green")
    d.arrow([(452, 120), (548, 168)], kind="red")
    d.text(380, 230, "the reason you pass to failure() appears in the Error report", "small")
    return d.render()


def step_shape():
    d = new("step-shape", 760, 260, "A step load shape",
            "A LoadTestShape adds a few users every few seconds, so you can see at which step response times start to climb.")
    d.line(60, 200, 700, 200)
    d.line(60, 30, 60, 200)
    for i, (x, h) in enumerate([(60, 40), (240, 80), (420, 120)]):
        d.rect(x, 200 - h, 180, h, "blue" if i < 2 else "green", rx=0)
        d.text(x + 90, 200 - h / 2, f"{(i + 1) * 2} users", "bold")
        d.text(x + 90, 218, f"{i * 3}-{i * 3 + 3} s", "small")
    d.text(380, 245, "step_time = 3 s, +2 users per step, total_time = 9 s", "small")
    return d.render()


def distributed():
    d = new("locust-distributed", 760, 280, "Master and workers",
            "The master hands out users and collects results. Workers generate the load. Add workers (even on other computers) to add load.")
    d.box(290, 20, 180, 60, [("Master", "bold"), ("--master", "code")], "amber")
    for i, x in enumerate((60, 290, 520)):
        d.box(x, 150, 180, 60, [(f"Worker {i + 1}", "bold"), ("--worker", "code")], "blue")
        d.arrow([(x + 90, 148), (380, 82)], kind="blue")
    d.box(240, 235, 280, 36, [("Your service", "bold")], "green")
    for x in (150, 380, 610):
        d.arrow([(x, 212), (380, 234)], kind="green")
    return d.render()


if __name__ == "__main__":
    fns = [load_idea, user_loop, wait_types, lifecycle, http_flow, validate, step_shape, distributed]
    for fn in fns:
        fn()
    print(len(fns), "diagrams written")
