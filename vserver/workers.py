import asyncio
import logging
from typing import Dict

import aiohttp

import settings
from connection import connection
from rpc import rpc
from worker import Worker

log = logging.getLogger(__name__)


class Workers:
    def __init__(self):
        self.workers: Dict[str, Worker] = {}
        self._last_update_workers_status: float = 0
        self._last_update_workers: float = 0

    def delete_workers(self):
        for worker in self.workers:
            del worker

    async def get_workers(self):
        workers: Dict[int, Worker] = {}

        try:
            async with connection.session.get(f'http://{settings.REST_IP}:{settings.REST_PORT}/workers/') as response:
                for worker in await response.json():
                    workers[worker['ip']] = Worker(
                        worker['ip'],
                        worker['login'],
                        worker['password'],
                        worker['accounts'],
                        worker['proxies'])

                return workers

        except aiohttp.ClientConnectorError:
            log.warning('ClientConnectorError')

        except Exception:
            log.exception('Error')

        return workers

    async def init(self):
        task = asyncio.ensure_future(self.update_workers())
        task = asyncio.ensure_future(self.update_workers_status())

    async def update_workers(self):
        def time_passed():
            return asyncio.get_event_loop().time() - self._last_update_workers

        while True:
            if time_passed() > settings.INTERVAL_UPDATE_WORKERS:
                log.debug('start update_workers')

                workers = await self.get_workers()
                if workers:
                    difference = set(workers.keys() ^ self.workers.keys())
                    if difference:
                        self.workers = workers
                else:
                    self.delete_workers()

                self._last_update_workers_status = asyncio.get_event_loop().time()

                log.debug('end update_workers')

            await asyncio.sleep(settings.INTERVAL_UPDATE_WORKERS)

    # async def update_workers_status(self):
    #     def time_passed():
    #         return asyncio.get_event_loop().time() - self._last_update_workers_status
    #
    #     while True:
    #         if time_passed() > settings.INTERVAL_UPDATE_WORKERS_STATUS:
    #             log.debug('start update_workers_status')
    #
    #             tasks = [asyncio.create_task(rpc.call(worker.ip, 'application.status')) for worker in
    #                      self.workers.values()]
    #             if tasks:
    #                 done, pending = await asyncio.wait(tasks, timeout=30)
    #
    #                 for task in done:
    #                     result = task.result()
    #                     self.workers[result['ip']].status = result['result']
    #
    #             self._last_update_workers_status = asyncio.get_event_loop().time()
    #
    #             log.debug('end update_workers_status')
    #
    #         await asyncio.sleep(settings.INTERVAL_UPDATE_WORKERS_STATUS)
