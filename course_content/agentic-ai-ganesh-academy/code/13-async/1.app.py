import asyncio


async def make_tea():
    print("Boiling water...")
    await asyncio.sleep(3)  # time taking process.
    print("Tea is ready!")


async def make_toast():
    print("Toasting bread...")
    await asyncio.sleep(2)
    print("Toast is ready!")


async def main():
    await asyncio.gather(make_toast(), make_tea())


asyncio.run(main())
