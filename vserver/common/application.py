from enum import Enum, auto
from typing import NamedTuple


class ApplicationStatus(Enum):
    AUTH_LOGIN_OR_PASSWORD_INCORRECT = 'Логин или пароль неверны'
    SERVER_NOT_RESPONSE = 'Ошибка. Vtope сервер не отвечает'
    CLIENT_NOT_RESPONSE = 'Клиент не работает'
    NOT_AUTH = 'Vtope bot не авторизован'
    READY = 'Vtope bot готов к работе'
    WORK = 'Vtope bot работает'
    STOP = 'Vtope bot закрыт'
    ERROR = 'Ошибка VBot'


class ApplicationAuthParameters(NamedTuple):
    login: str
    password: str


class ApplicationStartStatus(Enum):
    ERROR_ALREADY_START = 'Ошибка. Vtope bot уже запущен'
    ERROR = 'Неизвестная ошибка'
    START = 'Vtope bot запущен'


class ApplicationStopStatus(Enum):
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
