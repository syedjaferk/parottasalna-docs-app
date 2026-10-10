import asyncio


async def hello():
    print("Hello")

    await asyncio.sleep(2)

    print("World")


asyncio.run(hello())
