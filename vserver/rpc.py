import asyncio
import logging
import pickle
from typing import Any, NamedTuple

from aio_pika import RobustQueue, IncomingMessage, Message

from common.common import CommandMessage, ResultMessage
from connection import connection

log = logging.getLogger(__name__)

#TODO Сделать удаление если клиент отключен и проверить на exception

class RPC:
    RESULT_QUEUE = 'worker'

    def __init__(self):
        self.result_queue: RobustQueue = None
        self.futures = dict()

    async def init(self):
        self.result_queue = await connection.channel.declare_queue(self.RESULT_QUEUE, auto_delete=True, exclusive=True)
        await self.result_queue.consume(self.on_result_message)

    async def on_result_message(self, message: IncomingMessage):
        correlation_id = int(message.correlation_id) if message.correlation_id else None

        await message.ack()

        future: asyncio.Future = self.futures.pop(correlation_id, None)

        if future is None:
            log.warning("Unknown message: %r", message)
            return

        try:
            result: ResultMessage = self.deserialize(message.body)
        except pickle.UnpicklingError:
            log.error("Failed to deserialize response on message: %r", message)
            future.set_exception(Exception(correlation_id))
            return

        if isinstance(result, ResultMessage):
            future.set_result(result)
        else:
            log.error('Message is not ResultMessage \n %r', result)
            future.set_exception(Exception(correlation_id))

    async def call(self, worker_ip: str, command: str, parameters: NamedTuple = None):
        future = await self.create_future()

        message = CommandMessage(command, parameters)

        message = Message(body=self.serialize(message), reply_to=self.RESULT_QUEUE, correlation_id=id(future))

        await connection.exchange.publish(message, routing_key=worker_ip)

        return await future

    @staticmethod
    def deserialize(data: bytes) -> Any:
        return pickle.loads(data)

    @staticmethod
    def serialize(data: Any) -> bytes:
        return pickle.dumps(data)

    async def create_future(self) -> asyncio.Future:
        future = asyncio.Future()

        self.futures[id(future)] = future

        return future


rpc = RPC()
