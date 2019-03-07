import asyncio

from peewee import DoesNotExist

from vserver.worker import Worker


class Workers:
    def __init__(self):
        self.workers = None

    async def init(self):
        try:
            self.workers = list(Worker.select())
        except DoesNotExist:
            self.workers = []

        await self.status()

    async def status(self):
        for worker in self.workers:
            await asyncio.ensure_future(worker.status())


workers = Workers()
