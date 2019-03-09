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



workers = Workers()
