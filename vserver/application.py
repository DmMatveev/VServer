from typing import List, Any, Coroutine

import aiohttp
from aio_pika import RobustQueue, IncomingMessage

from connection import connection
from rpc import rpc
from workers import Workers


class Application:
    def __init__(self):
        self.workers = Workers()
        self.server_queue: RobustQueue = None

    async def init(self):
        await connection.init()
        await rpc.init()

        await self.workers.init()

        self.server_queue = await connection.channel.declare_queue('server', auto_delete=True)


    async def start(self):
        await self.init()

        async with self.server_queue.iterator() as messages:
            message: IncomingMessage
            async for message in messages:
                async with message.process():
                    print(message.body)

