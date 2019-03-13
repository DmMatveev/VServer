from dataclasses import dataclass
from typing import List, Dict

from rpc import rpc
from status import *


# TODO можно заменить rpc.call на wraps(rpc.call, self.ip)


class Account:
    def __init__(self, login: str, password: str):
        self.login = login
        self.password = password


class Proxy:
    def __init__(self, ip: str, port: int, login: str = None, password: str = None):
        self.ip = ip
        self.port = port
        self.login = login
        self.password = password

@dataclass
class Worker:
    ip: str
    login: str
    password: str
    accounts: List[Account]
    proxies: List[Proxy]

    def __init__(self, ip: str, login: str, password: str, accounts: List, proxies: List):
        self.ip = ip
        self.login = login
        self.password = password
        self.accounts: List[Account] = self.init_accounts(accounts)
        self.proxies: List[Proxy] = self.init_proxies(proxies)
        self.last_update_status = 0

        self._status: Dict = None

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

    async def auth(self):
        if self.info[self.APP_STATUS] == WorkerStatus.NOT_AUTH:
            arguments = {
                'app_login': self.login,
                'app_password': self.password
            }

            result = await rpc.call(self.ip, 'application.auth', arguments)

            if result == AuthStatus.AUTH:
                self.info[self.AUTH_STATUS] = AuthStatus.AUTH
                await self.status()

            elif result == AuthStatus.ERROR_LOGIN_OR_PASSWORD_INCORRECT:
                self.info[self.AUTH_STATUS] = AuthStatus.ERROR_LOGIN_OR_PASSWORD_INCORRECT

            elif result == AuthStatus.ERROR_SERVER_NOT_RESPONSE:
                self.info[self.AUTH_STATUS] = AuthStatus.ERROR_SERVER_NOT_RESPONSE

            elif result == AuthStatus.ERROR_ALREADY_AUTH:
                pass  # debug

            self.info[self.AUTH_STATUS] = AuthStatus.ERROR

    async def stop(self):
        result = await rpc.call(self.ip, 'application.stop')
        if result == StopStatus.STOP:
            await self.status()
        else:
            pass  # debug

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
