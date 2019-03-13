import asyncio
import logging
import pickle
from typing import Any

from aio_pika import RobustQueue, IncomingMessage, Message

from connection import connection

log = logging.getLogger(__name__)


class RPC:
    RESULT_QUEUE = 'worker'

    def __init__(self):
        self.result_queue: RobustQueue = None
        self.futures = dict()

    async def _create_future(self) -> asyncio.Future:
        future = asyncio.Future()
        self.futures[id(future)] = future

        return future

    async def init(self):
        self.result_queue = await connection.channel.declare_queue(self.RESULT_QUEUE, auto_delete=True)
        await self.result_queue.consume(self.on_result_message)

    async def on_result_message(self, message: IncomingMessage):
        correlation_id = int(message.correlation_id) if message.correlation_id else None

        future: asyncio.Future = self.futures.pop(correlation_id, None)

        if future is None:
            log.warning("Unknown message: %r", message)
            return

        try:
            data = self.deserialize(message.body)
        except pickle.UnpicklingError as e:
            log.error("Failed to deserialize response on message: %r", message)
            future.set_exception(e)
            return
        #namedtuple
        data = {
            'result': data,
            'ip': message.app_id
        }

        future.set_result(data)

    async def call(self, worker_ip: str, command: str, arguments: dict = None) -> asyncio.Future:
        future = await self._create_future()

        data = {
            'command': command,
            'arguments': arguments
        }

        message = Message(body=self.serialize(data), reply_to=self.RESULT_QUEUE, correlation_id=id(future))

        await connection.exchange.publish(message, routing_key=worker_ip)

        return await future

    async def register_worker(self, worker_ip: str):
        await connection.channel.declare_queue(worker_ip, auto_delete=True)

    def deserialize(self, data: bytes) -> Any:
        return pickle.loads(data)

    def serialize(self, data: Any) -> bytes:
        return pickle.dumps(data)


rpc = RPC()
