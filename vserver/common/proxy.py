from enum import Enum, auto
from typing import NamedTuple


class ProxyType(Enum):
    HTTPS = auto()  # Обязательно перед HTTP, проходит проверка в in
    HTTP = auto()
    SOCKS5 = auto()


class ProxyStatus(Enum):
    badstate = 'Прокси не работает'
    validating = 'Валидация'
    queued = 'В очереди на работу'
    working = 'В работе'
    badproxy = 'Нерабочий прокси'


class ProxyInfo(NamedTuple):
    ip: str
    port: int
    status: ProxyStatus
    type: ProxyType


class ProxyAddParameters(NamedTuple):
    ip: str
    port: int
    type: ProxyType
    login: str = ''
    password: str = ''


class ProxyDeleteParameters(NamedTuple):
    ip: str
