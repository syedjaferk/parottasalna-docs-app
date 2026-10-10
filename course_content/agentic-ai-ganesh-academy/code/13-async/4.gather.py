import asyncio
import time


async def task(name, seconds):
    print(f"{name} started")

    await asyncio.sleep(seconds)

    print(f"{name} completed")


async def main():
    start = time.perf_counter()

    await asyncio.gather(
        task("Task 1", 2),
        task("Task 2", 2),
        task("Task 3", 2),
    )

    end = time.perf_counter()

    print(f"Total time: {end - start:.2f} seconds")


asyncio.run(main())
