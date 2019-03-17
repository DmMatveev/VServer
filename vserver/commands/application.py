from symbol import parameters

from common.account import AccountAddParameters
from common.common import ResultMessage, AuthStatus, ApplicationAuthParameters


class Application:
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
            self.state.worker_current_command = 'Авторизация'
            self.state.worker_current_command_status = 'Выполянется'

            result = await self.call_command('application.auth', ApplicationAuthParameters(self.login, self.password))

            self.state.worker_current_command_status = result.status.value

            return result

        self.state.worker_current_command_status = AuthStatus.ERROR_LOGIN_OR_PASSWORD_INCORRECT.value

        return ResultMessage(AuthStatus.ERROR_LOGIN_OR_PASSWORD_INCORRECT)
