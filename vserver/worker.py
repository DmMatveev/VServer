import logging
from dataclasses import dataclass
from typing import List

from common import *
from connection import connection
from rpc import rpc

log = logging.getLogger(__name__)


@dataclass
class Account:
    login: str
    password: str


@dataclass
class Proxy:
    ip: str
    port: int
    login: str = ''
    password: str = ''


class State:
    code = None

    def __init__(self):
        self.worker_status = ''
        self.worker_current_command = ''
        self.worker_current_command_status = ''

    def __setattr__(self, key, value):
        if key in ['worker_status', 'worker_current_command', 'worker_current_command_status']:
            connection.redis.hset(self.code, key, value)
            connection.redis.expire(self.code, 60)
            return

        raise AttributeError


class Worker:
    def __init__(self, id: int, ip: str, login: str, password: str,
                 accounts: List[Dict[str, str]],
                 proxies: List[Dict[str, str]]):
        self.code = id
        self.ip = ip
        self.login = login
        self.password = password
        self.accounts: List[Account] = [Account(**account) for account in accounts]
        self.proxies: List[Proxy] = [Proxy(**proxy) for proxy in proxies]

        self.last_update_status = 0

        self.is_work = False
        self.is_auth = False
        State.code = self.code
        self.state = State()

    async def init(self):
        if not self.is_work:
            self.state.worker_status = 'Инициализация'

            await self.stop()
            await self.start()

            result = await self.status()

            if result.status != WorkerStatus.STOP:
                self.is_work = True
            else:
                return

            if result.status == WorkerStatus.READY or result.status == WorkerStatus.WORK:
                self.is_auth = True

        if self.is_work and not self.is_auth:
            result = await self.auth()
            if result.status == AuthStatus.AUTH:
                await self.status()
                self.is_auth = True

    def update(self, id: int, ip: str, login: str, password: str,
               accounts: List[Dict[str, str]],
               proxies: List[Dict[str, str]]):

        if self.login != login or self.password != password:
            self.login = login
            self.password = password

    async def status(self) -> ResultMessage:
        self.state.worker_current_command = 'Статус'
        self.state.worker_current_command_status = 'Выполняется'

        result = await self.call_command('application.status')

        self.state.worker_status = result.status.value

        self.state.worker_current_command = ''
        self.state.worker_current_command_status = ''

        return result

    async def start(self) -> ResultMessage:
        self.state.worker_current_command = 'Старт'
        self.state.worker_current_command_status = 'Выполняется'

        result = await self.call_command('application.start')

        self.state.worker_current_command_status = result.status.value
        return result

    async def stop(self) -> ResultMessage:
        self.state.worker_current_command = 'Стоп'
        self.state.worker_current_command_status = 'Выполняется'

        result = await self.call_command('application.stop')

        self.state.worker_current_command_status = result.status.value

        return result

    async def auth(self) -> ResultMessage:
        if self.login and self.password:
            parameters = {
                'login': self.login,
                'password': self.password
            }
            self.state.worker_current_command = 'Авторизация'
            self.state.worker_current_command_status = 'Выполянется'

            result = await self.call_command('application.auth', parameters)

            self.state.worker_current_command_status = result.status.value

            return result

        self.state.worker_current_command_status = AuthStatus.ERROR_LOGIN_OR_PASSWORD_INCORRECT.value

        return ResultMessage(AuthStatus.ERROR_LOGIN_OR_PASSWORD_INCORRECT)

    async def call_command(self, command: str, parameters: Dict[str, str] = None) -> ResultMessage:
        return await rpc.call(self.ip, command, parameters)
