from enum import auto, Enum

from vserver.db import WorkerDBMixin
from vserver.rpc import rpc


class Status(Enum):
    NOT_AUTH = auto()
    STOP = auto()
    READY = auto()
    WORK = auto()
    ERROR = auto()


class Worker(WorkerDBMixin):
    async def get_status(self):
        result = await rpc.call('application.status', self.ip)

        self.status = {'status': result}

        self.save()


    def auth(self):
        pass

    def stop(self):
        pass

    def start(self):
        pass

    def reset(self):
        pass

    def reboot(self):
        pass

    def add_account(self):
        pass

    def delete_account(self):
        pass
