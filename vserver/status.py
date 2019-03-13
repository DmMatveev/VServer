from enum import Enum, auto


class WorkerStatus(Enum):
    NOT_AUTH = auto()
    READY = auto()
    STOP = auto()
    WORK = auto()


class AuthStatus(Enum):
    ERROR_LOGIN_OR_PASSWORD_INCORRECT = auto()
    ERROR_SERVER_NOT_RESPONSE = auto()
    ERROR_ALREADY_AUTH = auto()
    ERROR = auto()
    AUTH = auto()


class StartStatus(Enum):
    ERROR_ALREADY_START = auto()
    ERROR = auto()
    START = auto()


class StopStatus(Enum):
    ERROR = auto()
    STOP = auto()


class ResetStatus(Enum):
    ERROR_APP_START = auto()
    ERROR = auto()
    RESET = auto()
