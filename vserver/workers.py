import asyncio
import logging
from typing import Dict

import aiohttp

import settings
from connection import connection
from worker import Worker

log = logging.getLogger(__name__)


class Workers:
    def __init__(self):
        self.workers: Dict[str, Worker] = {}
        self._last_update_workers: float = 0

    async def init(self):
        await asyncio.ensure_future(self.update_workers())

    def delete_workers(self, worker_codes):
        for worker_code in worker_codes:
            del self.workers[worker_code]

    def add_workers(self, workers, worker_codes):
        for worker_code in worker_codes:
            for worker in workers:
                if worker['id'] == worker_code:
                    self.workers[worker_code] = Worker(**worker)
                    break

    def get_add_worker_codes(self, workers):
        return set([int(worker['id']) for worker in workers]) - set(self.workers.keys())

    def get_delete_worker_codes(self, workers):
        return set(self.workers.keys()) - set([int(worker['id']) for worker in workers])

    async def update_workers(self):
        while True:
            log.debug('start update_workers')

            workers = await self.get_workers()
            if workers is None:
                log.error('Нет ни одного воркера')

            if workers:
                delete_worker_codes = self.get_delete_worker_codes(workers)
                self.delete_workers(delete_worker_codes)

                add_worker_codes = self.get_add_worker_codes(workers)
                self.add_workers(workers, add_worker_codes)

                await asyncio.gather(*[worker.init() for worker in self.workers.values()])

                #for worker in workers:
                #    await self.workers[worker['id']].update(**worker)

            log.debug('end update_workers')

            await asyncio.sleep(settings.INTERVAL_UPDATE_WORKERS)

    async def get_workers(self):
        try:
            async with connection.session.get(f'http://{settings.REST_IP}:{settings.REST_PORT}/workers/') as response:
                return await response.json()

        except aiohttp.ClientConnectorError:
            log.error('ClientConnectorError')

        except Exception:
            log.exception('Error')

        return None

    def delete_all_workers(self):
        for worker in self.workers:
            del worker
