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
        self.workers: Dict[str, Worker] = []

    async def init(self):
        await asyncio.create_task(self.update_workers())

    async def update_workers(self):
        while True:
            workers = await self.get_workers()
            if workers:
                try:
                    workers_remove = set(self.workers.keys()) - set(workers.keys())
                    if workers_remove:
                        log.info('Delete workers %s', workers_remove)
                        pass

                    workers_add = set(workers.keys()) - set(self.workers.keys())
                    if workers_add:
                        for worker in workers_add:
                            log.info('Add worker %s', worker)
                            self.workers[worker] = Worker(workers[worker].pop('code'), workers[worker]['name'])

                    log.debug('Update workers %s', self.workers.keys())

                    tasks = []
                    for worker_name, worker in self.workers.items():
                        tasks.append(worker.update(**workers[worker_name]))

                    await asyncio.gather(*tasks, return_exceptions=True)

                except AttributeError:
                    continue

            await asyncio.sleep(settings.INTERVAL_UPDATE_WORKERS)

    async def get_workers(self) -> Dict[str, Dict]:
        workers = []

        try:
            async with connection.session.get(f'http://{settings.REST_IP}:{settings.REST_PORT}/workers/') as response:
                workers = await response.json()

        except aiohttp.ClientConnectorError:
            log.exception('aiohttp.ClientConnectorError')

        # TODO В будущем сузить круг исключений. Проверить на не json формат
        except Exception:
            log.exception('aiohttp.Exception')

        finally:
            return workers
