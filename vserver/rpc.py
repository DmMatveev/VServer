import asyncio
import pickle
from enum import Enum, unique
from typing import Any

from aiormq.types import DeliveredMessage

from pamqp import specification

from vserver.connection import connection


@unique
class RPCMessageTypes(Enum):
    error = 'error'
    result = 'result'
    call = 'call'


class RPC:
    RESULT_QUEUE = 'worker'

    def __init__(self):
        self.result_queue = None
        self.futures = dict()

    async def _create_future(self) -> asyncio.Future:
        future = asyncio.Future()
        self.futures[id(future)] = future

        return future

    async def init(self):
        if self.result_queue is not None:
            return

        self.result_queue = await connection.channel.queue_declare(self.RESULT_QUEUE, auto_delete=True)

        await connection.channel.basic_consume(self.RESULT_QUEUE, self.on_result_message)

    async def on_result_message(self, message: DeliveredMessage):
        properties = message.header.properties

        correlation_id = int(properties.correlation_id) if properties.correlation_id else None

        future: asyncio.Future = self.futures.pop(correlation_id, None)

        if future is None:
            # log.warning("Unknown message: %r", message)
            return

        try:
            data = self.deserialize(message.body)
        except Exception as e:
            # log.error("Failed to deserialize response on message: %r", message)
            future.set_exception(e)
            return

        if properties.message_type == RPCMessageTypes.result.value:
            future.set_result(data)

        elif properties.message_type == RPCMessageTypes.error.value:
            future.set_exception(data)

        elif properties.message_type == RPCMessageTypes.call.value:
            future.set_exception(
                asyncio.TimeoutError("Message timed-out", message)
            )
        else:
            future.set_exception(
                RuntimeError("Unknown message type %r" % message.type)
            )

    def deserialize(self, data: bytes) -> Any:
        return pickle.loads(data)

    def serialize(self, data: Any) -> bytes:
        return pickle.dumps(data)

    async def call(self, worker_name: str, command: str, arguments: dict = None) -> asyncio.Future:
        future = await self._create_future()

        properties = specification.Basic.Properties(reply_to=self.RESULT_QUEUE, correlation_id=str(id(future)))

        data = {
            'command': command,
            'arguments': arguments
        }

        await connection.channel.basic_publish(self.serialize(data), routing_key=worker_name, properties=properties)

        return await future

    async def register_worker(self, worker_name: str):
        await connection.channel.queue_declare(worker_name, auto_delete=True)


rpc = RPC()
