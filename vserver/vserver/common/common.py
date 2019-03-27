from enum import Enum, auto
from typing import NamedTuple, List


class CommandMessage(NamedTuple):
    command: str
    parameters: NamedTuple = None


class CommandStatus(Enum):
    SUCCESS = auto()
    ERROR = auto()
    INVALID = auto()


class ResultMessage(NamedTuple):
    status: CommandStatus
    data: List[Enum] = None
