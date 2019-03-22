import asyncio
import logging
from dataclasses import dataclass, asdict
from typing import Dict, NamedTuple, NewType

from common.account import AccountStatus, AccountType, AccountAddParameters
from common.application import ApplicationStatus, ApplicationAuthParameters
from common.common import ResultMessage, CommandStatus
from common.proxy import ProxyStatus, ProxyType, ProxyAddParameters, ProxyInfo, ProxyDeleteParameters
from rpc import rpc

log = logging.getLogger(__name__)


@dataclass
class Proxy:
    ip: str
    port: int
    login: str = ''
    password: str = ''
    type: ProxyType = ProxyType.HTTPS
    status: ProxyStatus = None


@dataclass
class Account:
    login: str
    password: str
    type: AccountType = AccountType.INSTAGRAM
    status: AccountStatus = None
    proxy: str = ''


Accounts = NewType('Accounts', Dict[str, Account])
Proxies = NewType('Proxies', Dict[str, Proxy])


class Worker:
    def __init__(self, code: int, name: str):
        self.code: int = code
        self.name: str = name
        self.login: str = None
        self.password: str = None
        self.accounts: Accounts = []
        self.proxies: Proxies = []

        self.status: ApplicationStatus = None

        self.count_errors = 0

    async def update(self,
                     name: str,
                     login: str,
                     password: str,
                     accounts: Dict[str, Dict],
                     proxies: Dict[str, Dict]):

        if name != self.name:
            await self.call_command('application.update')
            return

        await self.update_status()

        if self.status == ApplicationStatus.STOP:
            await self.call_command('application.stop')
            await self.call_command('application.start')

            await self.update_status()

        if self.status == ApplicationStatus.NOT_AUTH or self.status == ApplicationStatus.AUTH_LOGIN_OR_PASSWORD_INCORRECT:
            result = await self.call_command('application.auth',
                                             ApplicationAuthParameters(login, password))

            self.login = login
            self.password = password

            await self.update_status()

        if self.status == ApplicationStatus.READY or self.status == ApplicationStatus.WORK:
            if self.login != login or self.password != password:
                # выйти из аккаунта
                return

            proxies_add = set(proxies.keys()) - set(self.proxies.keys())
            if proxies_add:
                for proxy in proxies_add:
                    proxy = proxies[proxy]
                    proxy['port'] = int(proxy['port'])
                    proxy = Proxy(**proxy)
                    self.proxies[proxy.ip] = proxy

            accounts_add = set(accounts.keys()) - set(self.accounts.keys())
            if accounts_add:
                for account in accounts_add:
                    account = accounts[account]
                    account = Account(**account)
                    self.accounts[account.login] = account

            result = await self.call_command('proxy.list')
            if result.status == CommandStatus.SUCCESS:
                proxies_add = set(self.proxies.keys()) - set(map(lambda x: x.ip, result.data))
                if proxies_add:
                    for proxy_ip in proxies_add:
                        proxy = self.proxies[proxy_ip]
                        parameters = ProxyAddParameters(proxy.ip,
                                                        proxy.port,
                                                        proxy.type,
                                                        proxy.login,
                                                        proxy.password)
                        await self.call_command('proxy.add', parameters)

                for proxy in result.data:
                    self.proxies[proxy.ip].status = proxy.status

                for proxy in self.proxies.values():
                    if proxy.status == ProxyStatus.badstate or proxy.status == ProxyStatus.badproxy:
                        await self.call_command('proxy.delete', ProxyDeleteParameters(proxy.ip))

            else:
                log.error(f'VBot(%s) command proxy.list has error', self.name)
                return

            result = await self.call_command('account.list')
            if result.status == CommandStatus.SUCCESS:
                accounts_add = set(self.accounts.keys()) - set(map(lambda x: x.login, result.data))
                if accounts_add:
                    for account_login in accounts_add:
                        account = self.accounts[account_login]
                        proxy_status = self.proxies[account.proxy].status
                        if proxy_status == ProxyStatus.queued or proxy_status == ProxyStatus.working:
                            parameters = AccountAddParameters(account.login,
                                                              account.password,
                                                              AccountType.INSTAGRAM,
                                                              account.proxy)
                            await self.call_command('account.add', parameters)

                for account in result.data:
                    self.accounts[account.login].status = account.status

            else:
                log.error(f'VBot(%s) command account.list has error', self.name)
                return

    async def update_status(self):
        result = await self.call_command('application.status', timeout=90)
        if result.status == CommandStatus.SUCCESS:
            self.status = result.data

        elif result.status == CommandStatus.ERROR:
            raise RuntimeError(f'VBot({self.name}) command application.status has error')

    async def call_command(self, command: str, parameters: NamedTuple = None, timeout: int = 180) -> ResultMessage:
        log.info('Worker(%s) send command: %s', self.name, command)

        try:
            return await asyncio.wait_for(rpc.call(self.name, command, parameters), timeout=timeout)
        except asyncio.TimeoutError:
            self.status = ApplicationStatus.CLIENT_NOT_RESPONSE
            log.error('VBot(%s) not response', self.name)
            raise RuntimeError
