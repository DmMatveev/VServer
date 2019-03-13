from enum import Enum, auto
from typing import Dict, Any, NamedTuple


class CommandMessage(NamedTuple):
    command: str
    parameters: Dict[str, str] = None


class ResultMessage(NamedTuple):
    status: Any
    data: Dict[str, str] = None


class WorkerStatus(Enum):
    NOT_AUTH = auto()
    READY = auto()
    STOP = auto()
    WORK = auto()


class StartStatus(Enum):
    ERROR_ALREADY_START = auto()
    ERROR = auto()
    START = auto()


class StopStatus(Enum):
    ERROR = auto()
    STOP = auto()


class AuthStatus(Enum):
    ERROR_LOGIN_OR_PASSWORD_INCORRECT = auto()
    ERROR_SERVER_NOT_RESPONSE = auto()
    ERROR_ALREADY_AUTH = auto()
    ERROR = auto()
    AUTH = auto()


class ResetStatus(Enum):
    ERROR_APP_START = auto()
    ERROR = auto()
    RESET = auto()
