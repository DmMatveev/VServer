import asyncio

from application import Application


async def init():
    application = Application()
    await application.init()


if __name__ == '__main__':
    asyncio.run(init(), debug=True)
