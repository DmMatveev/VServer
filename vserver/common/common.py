from enum import Enum, auto
from typing import NamedTuple


class CommandMessage(NamedTuple):
    command: str
    parameters: NamedTuple = None


class ResultMessage(NamedTuple):
    status: Enum
    data: Enum = None


class ApplicationAuthParameters(NamedTuple):
    login: str
    password: str



class WorkerStatus(Enum):
    NOT_AUTH = 'Vtope bot не авторизован'
    READY = 'Vtope bot готов к работе'
    STOP = 'Vtope bot закрыт'
    WORK = 'Vtope bot работает'


class StartStatus(Enum):
    ERROR_ALREADY_START = 'Ошибка. Vtope bot уже запущен'
    ERROR = 'Неизвестная ошибка'
    START = 'Vtope bot запущен'


class StopStatus(Enum):
    ERROR = 'Неизвестная ошибка'
    STOP = 'Vtope bot закрыт'


class AuthStatus(Enum):
    ERROR_LOGIN_OR_PASSWORD_INCORRECT = 'Ошибка. Логин или пароль неверны'
    ERROR_SERVER_NOT_RESPONSE = 'Ошибка. Сервер не отвечает'
    ERROR_ALREADY_AUTH = 'Ошибка. Vtope bot уже авторизован'
    ERROR = 'Неизвестная ошибка'
    AUTH = 'Авторизация прошла успешна'


class ResetStatus(Enum):
    ERROR_APP_START = auto()
    ERROR = auto()
    RESET = auto()

