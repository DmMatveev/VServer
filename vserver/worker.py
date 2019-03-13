import logging
from dataclasses import dataclass
from typing import List, Dict, Any

import redis

from rpc import rpc

from status import *

log = logging.getLogger(__name__)


# TODO можно заменить rpc.call на wraps(rpc.call, self.ip)

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




class Worker:
    # ip: str
    # login: str
    # password: str
    # accounts: List[Account]
    # proxies: List[Proxy]

    def __init__(self, ip: str, login: str, password: str, accounts: List, proxies: List):
        self.ip = ip
        self.login = login
        self.password = password
        self.accounts: List[Account] = self.init_accounts(accounts)
        self.proxies: List[Proxy] = self.init_proxies(proxies)
        self.last_update_status = 0

        self.isInit = False

        '''
            status: str,
            data: dict,
            count_command
            current_command
            
        '''

        self._status: Dict = None

    async def init(self):
        status = await self.get_status()

        if not (status in WorkerStatus):
            log.error('status in WorkerStatus', status)
            return  # Не нее

        if status == WorkerStatus.STOP:
            result = await self.stop()

            result = await self.call_command('application.start')
            if result is None:
                return

        if status == WorkerStatus.NOT_AUTH:
            result = await self.call_command(
                'application.auth',
                AuthParameters(self.login, self.password)
            )

    async def call_command(self, command: str, arguments: Any = None):
        return await rpc.call(self.ip, command, arguments)

    async def get_status(self):
        result = await self.call_command('application.status')

        return result

    def set_status(self):

    def init_accounts(self, accounts: List) -> List[Account]:
        result: List[Account] = []
        for account in accounts:
            result.append(Account(account['login'], account['password']))

        return result

    def init_proxies(self, proxies: List) -> List[Proxy]:
        result: List[Proxy] = []
        for proxy in proxies:
            result.append(Proxy(proxy['login'], proxy['port'], proxy['login'], proxy['password']))

        return result

    @property
    def status(self):
        return self.status

    @status.setter
    def status(self, value):
        self._status = value
        # redis.set(self.ip, status)

    async def auth(self):
        if self.status == WorkerStatus.NOT_AUTH:
            parameters = AuthParameters(self.login, self.password)
            result = await self.call_command('application.auth', parameters)

            status = result.status

            if self._check_incoming_status(result.status, AuthStatus):
                #уставноить что сервер не работает

            if status == AuthStatus.AUTH:
                pass

            elif status == AuthStatus.ERROR_LOGIN_OR_PASSWORD_INCORRECT:
                pass

            elif status == AuthStatus.ERROR_SERVER_NOT_RESPONSE:
                pass

            elif status == AuthStatus.ERROR_ALREADY_AUTH:
                pass  # debug

    async def stop(self):
        result = await self.call_command('application.stop')
        if result == StopStatus.STOP:
            self.set_status(WorkerStatus.STOP)
        else:
            log.error('')

    async def start(self):
        result = await rpc.call(self.ip, 'application.start')
        if result == StartStatus.START:
            await self.status()
        else:
            pass  # debug

    async def reset(self):
        result = await rpc.call(self.ip, 'application.reset')
        if result == ResetStatus.RESET:
            await self.status()

    def reboot(self):
        pass

    async def add_account(self):
        result = await rpc.call(self.ip, 'account.add')

    def delete_account(self):
        pass

    def _check_incoming_status(self, status, type_status):
        if status in type_status:
            return False

        return True
