from connection import connection
from rpc import rpc
from workers import Workers


class Application:
    def __init__(self):
        self.workers = Workers()

    async def init(self):
        await connection.init()
        await rpc.init()
        await self.workers.init()
