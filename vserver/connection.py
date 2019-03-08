import asyncio

import aiormq
import peewee
from peewee_migrate import Router
import redis


class Connection:
    def __init__(self):
        self.connect: aiormq.Connection = None
        self.channel: aiormq.Channel = None

        self.db = peewee.PostgresqlDatabase(
            'server',
            host='localhost',
            user='postgres',
            password='password',
            port=5432
        )

        self.redis = redis.Redis()

        #router = Router(self.db)
        #router.create('migration12')
        #router.run('migration12')
        #router.run()

    async def init(self):
        if self.connect is not None:
            await self.close()

        self.connect = await aiormq.connect('amqp://guest:guest@localhost/')
        self.channel = await self.connect.channel()

    async def close(self):
        await self.connect.close()


connection: Connection = Connection()
