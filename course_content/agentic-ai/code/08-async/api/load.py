import asyncio
import time

import httpx


async def send_request(client, msg):
    resp = await client.post("http://localhost:8000/chat", json={"message": msg})
    print(resp.json())


async def main():
    start = time.time()
    async with httpx.AsyncClient(timeout=30) as client:
        await asyncio.gather(
            send_request(client, "Weather in Chennai?"),
            send_request(client, "Weather in Mumbai?"),
            send_request(client, "Time in Delhi?"),
        )
    print(f"\nTotal time: {time.time() - start:.2f}s")


asyncio.run(main())
