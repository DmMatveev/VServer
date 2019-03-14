import logging
from dataclasses import dataclass
from typing import List

import commands
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


class Worker(commands.Application):
    def __init__(self, id: int, ip: str, login: str, password: str, accounts: List[Dict[str, str]],
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

    async def update(self, id: int, ip: str, login: str, password: str, accounts: List[Dict[str, str]],
                     proxies: List[Dict[str, str]]):

        await self.status()

        if self.login != login or self.password != password:
            self.login = login
            self.password = password

        #await self.delete_accounts(self.get_delete_accounts_login(accounts))
        await self.add_accounts(accounts, self.get_add_accounts_login(accounts))

    async def add_accounts(self, accounts, add_accounts_login):
        for account in accounts:
            if account['login'] in add_accounts_login:
                account = Account(**account)
                self.accounts.append(account)

                result = await self.account_add(account.login, account.password)
                d = 2

    def get_add_accounts_login(self, accounts):
        return set(map(lambda x: x['login'], accounts)) - set(map(lambda x: x.login, self.accounts))

    async def account_add(self, login: str, password: str):
        parameters = AccountAddParameters(login, password)

        return await self.call_command('account.add', parameters)

    async def call_command(self, command: str, parameters: Dict[str, str] = None) -> ResultMessage:
        return await rpc.call(self.ip, command, parameters)












    async def delete_accounts(self, delete_accounts_login):
        for account in self.accounts:
            if account.login in delete_accounts_login:
                self.accounts.remove(account)

    def get_delete_accounts_login(self, accounts):
        return set(map(lambda x: x.login, self.accounts)) - set(map(lambda x: x['login'], accounts))
