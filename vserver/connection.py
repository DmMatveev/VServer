import aiohttp
from aio_pika import RobustChannel, RobustConnection, connect_robust, RobustExchange
from aiohttp import ClientSession

import settings


class Connection:
    def __init__(self):
        self.connect: RobustConnection = None
        self.channel: RobustChannel = None
        self.exchange: RobustExchange = None
        self.session: ClientSession = None

    async def init(self):
        self.connect = await connect_robust(
            host=settings.RABBIT_HOST,
            port=settings.RABBIT_PORT,
            login=settings.RABBIT_LOGIN,
            password=settings.RABBIT_PASSWORD
        )

        self.channel = await self.connect.channel()

        self.exchange = self.channel.default_exchange

        self.session = aiohttp.ClientSession()


connection: Connection = Connection()
