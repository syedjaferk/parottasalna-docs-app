import asyncio


async def get_user():
    await asyncio.sleep(2)
    return "User"


async def get_orders():
    await asyncio.sleep(3)
    return "Orders"


async def get_products():
    await asyncio.sleep(1)
    return "Products"


async def main():
    user, orders, products = await asyncio.gather(
        get_user(),
        get_orders(),
        get_products(),
    )

    print(user)
    print(orders)
    print(products)


asyncio.run(main())
