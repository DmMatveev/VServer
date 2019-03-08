from vserver.db import WorkerDBMixin
from vserver.rpc import rpc
from vserver.status import *


# TODO можно заменить rpc.call на wraps(rpc.call, self.ip)


class Worker(WorkerDBMixin):
    APP_STATUS = 'app_status'
    AUTH_STATUS = 'auth_status'
    ACCOUNTS_STATUS = 'accounts'

    async def status(self):
        result = await rpc.call(self.ip, 'application.status')
        self.info[self.APP_STATUS] = result
        self.save()

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
                pass#debug

            self.info[self.AUTH_STATUS] = AuthStatus.ERROR

    async def stop(self):
        result = await rpc.call(self.ip, 'application.stop')
        if result == StopStatus.STOP:
            await self.status()
        else:
            pass#debug

    async def start(self):
        result = await rpc.call(self.ip, 'application.start')
        if result == StartStatus.START:
            await self.status()
        else:
            pass#debug

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
