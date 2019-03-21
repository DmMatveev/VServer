from enum import Enum, auto
from typing import NamedTuple


class CommandMessage(NamedTuple):
    command: str
    parameters: NamedTuple = None


class CommandStatus(Enum):
    SUCCESS = auto()
    ERROR = auto()


class ResultMessage(NamedTuple):
    status: CommandStatus
    data: Enum = None
