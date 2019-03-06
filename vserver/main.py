import asyncio

from vserver.connection import connection
from vserver.rpc import rpc
from vserver.workers import workers


async def init():
    await connection.init()
    await rpc.init()
    await workers.init()

    d = 2


if __name__ == '__main__':
    asyncio.run(init())
