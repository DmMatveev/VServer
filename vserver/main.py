import asyncio

from application import Application


async def init():
    application = Application()
    await application.start()


if __name__ == '__main__':
    asyncio.run(init())
