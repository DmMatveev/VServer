from enum import Enum
from typing import NamedTuple


class AccountType(Enum):
    INSTAGRAM = 'Instagram'
    VK = 'VK'


class AccountStatus(Enum):
    badauth = 'Ошибка авторизации'
    validating = 'Валидация'
    manual = 'Ручная авторизация'
    working = 'В работе'
    sleeping = 'Спит'
    badproxy = 'Прокси не работает'
    waitproxy = 'Ожидает прокси'


class AccountInfo(NamedTuple):
    login: str
    status: AccountStatus
    type: AccountType


class AccountAddParameters(NamedTuple):
    login: str
    password: str
    type: AccountType
    proxy: str = ''


class AccountAddStatus(Enum):
    ERROR_NOT_ADD = 'Ошибка. Аккаунт не добавлен',
    ERROR = 'Неизвестная ошибка'
    ADD = 'Аккаунт успешно добавлен'
