# mini_scheduler.py - how a scheduler works inside: a loop that wakes up and checks the clock.
# This is a tiny version of what `hermes cron` does for you.
#
#   python mini_scheduler.py            # runs a demo job every 10 seconds, 3 times
import time
from datetime import datetime


def say_hello():
    print(f"  [{datetime.now():%H:%M:%S}] Job ran! (imagine: fetch news, send to Telegram)")


# Each job: a name, a function, and how many seconds between runs.
JOBS = [
    {"name": "hello", "run": say_hello, "every_seconds": 10, "next_run": time.time() + 10, "times_left": 3},
]


def main():
    print("Scheduler started. It checks the clock every second. Press Ctrl+C to stop.")
    while any(job["times_left"] > 0 for job in JOBS):
        now = time.time()
        for job in JOBS:
            if job["times_left"] > 0 and now >= job["next_run"]:
                job["run"]()
                job["times_left"] -= 1
                job["next_run"] = now + job["every_seconds"]
        time.sleep(1)                                   # wake up once per second
    print("All jobs finished.")


if __name__ == "__main__":
    main()
