import asyncio
import logging
from dataclasses import dataclass
from typing import Dict, NamedTuple

from common.account import AccountStatus, AccountType, AccountAddParameters
from common.application import ApplicationStatus, ApplicationAuthParameters
from common.common import ResultMessage, CommandStatus
from common.proxy import ProxyStatus, ProxyType, ProxyAddParameters, ProxyDeleteParameters
from connection import connection
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


class Worker:
    def __init__(self, code: int, ip: str, login: str, password: str, name: str, **kwargs):
        self.name: str = name
        self.code = code
        self.ip: str = ip
        self.login: str = login
        self.password: str = password
        self.accounts: Dict[str, Account] = {}
        self.proxies: Dict[str, Proxy] = {}

        self.status: ApplicationStatus = None

        self.count_errors = 0

    async def update(self,
                     login: str,
                     password: str,
                     accounts: Dict[str, Dict],
                     proxies: Dict[str, Dict], **kwargs):

        # await self.call_command('application.stop')
        # await self.call_command('application.reset')
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
                pass

            diff = set(map(lambda x: x['ip'], proxies)) - set(self.proxies.keys())

            for d in diff:
                for proxy in proxies:
                    if d == proxy['ip']:
                        self.proxies[proxy['ip']] = Proxy(**proxy)
                        break

            diff = set(map(lambda x: x['account_login'], accounts)) - set(self.accounts.keys())

            for i in range(len(proxies)):
                accounts[i]['proxy'] = proxies[i]['ip']

            for d in diff:
                for account in accounts:
                    if d == account['account_login']:
                        login = account['account_login']
                        password = account['account_password']
                        proxy = account['proxy']

                        self.accounts[login] = Account(login, password, proxy=proxy)

            accounts = (await self.call_command('account.list')).data
            proxies = (await self.call_command('proxy.list')).data

            for proxy in proxies:
                self.proxies[proxy.ip].status = proxy.status

            delete_proxy = []
            for proxy in self.proxies.values():
                proxy_status = proxy.status
                if proxy_status in (ProxyStatus.queued, ProxyStatus.working, ProxyStatus.validating, None):
                    continue
                else:
                    await self.call_command('proxy.delete', ProxyDeleteParameters(proxy.ip))
                    delete_proxy.append(proxy.ip)

            for proxy in delete_proxy:
                self.proxies.pop(proxy)

            diff = set(self.proxies.keys()) - set(map(lambda x: x.ip, proxies))

            i = 0
            for d in diff:
                proxy = self.proxies[d]
                await self.call_command('proxy.add',
                                        ProxyAddParameters(
                                            proxy.ip,
                                            proxy.port,
                                            proxy.type,
                                            proxy.login,
                                            proxy.password
                                        ))
                if i == 5:
                    break
                i += 1

            diff = set(self.accounts.keys()) - set(map(lambda x: x.login, accounts))

            i = 0
            for d in diff:
                account = self.accounts[d]
                proxy_status = self.proxies[account.proxy].status
                if proxy_status == ProxyStatus.queued or proxy_status == ProxyStatus.working:
                    await self.call_command('account.add',
                                            AccountAddParameters(
                                                account.login,
                                                account.password,
                                                AccountType.INSTAGRAM,
                                                account.proxy
                                            ))

                if i == 5:
                    break
                i += 1

    async def update_status(self):
        result = await self.call_command('application.status')
        if result.status == CommandStatus.SUCCESS:
            self.status = result.data

        elif result.status == CommandStatus.ERROR:
            raise RuntimeError(f'VBot({self.name}) command application.status has error')

    async def call_command(self, command: str, parameters: NamedTuple = None, timeout: int = 60) -> ResultMessage:
        log.info('Worker(%s) send command: %s', self.name, command)

        await connection.session.post(f'http://212.109.195.39:8000/workers/{self.code}/logs/',
                                      data={'log': f'Command {command}'})

        try:
            result = await asyncio.wait_for(rpc.call(self.ip, command, parameters), timeout=timeout)

            log.info('Worker(%s) recieved result command: %s', self.name, result.status)

            await connection.session.post(f'http://212.109.195.39:8000/workers/{self.code}/logs/',
                                          data={'log': f'Result {result.status.name}\n'})


            return result

        except asyncio.TimeoutError:
            self.status = ApplicationStatus.CLIENT_NOT_RESPONSE
            log.error('VBot(%s) not response', self.ip)
            await connection.session.post(f'http://212.109.195.39:8000/workers/{self.code}/logs/', data={'log': 'Not response\n'})
            raise RuntimeError
