import asyncio

import httpx


async def fetch(client, url):
    print(f"Requesting {url}")

    response = await client.get(url)

    print(f"{url} → {response.status_code}")

    return response.status_code


async def main():
    urls = [
        "https://example.com",
        "https://httpbin.org/get",
        "https://httpbin.org/uuid",
    ]

    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(*(fetch(client, url) for url in urls))

    print(results)


asyncio.run(main())
