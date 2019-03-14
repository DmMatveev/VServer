from typing import Dict

from connection import connection


class State:
    states: Dict[str, 'State'] = {}

    def __init__(self, ip: str):
        self.ip = ip
        self.worker_status = ''
        self.worker_current_command = ''
        self.worker_current_command_status = ''

    @classmethod
    def init(cls, ip: str):
        if ip not in cls.states.keys():
            cls.states[ip] = cls(ip)
            return cls.states[ip]

    def __setattr__(self, key, value):
        if key in ['worker_status', 'worker_current_command', 'worker_current_command_status']:
            connection.redis.hset(self.ip, key, value)
            connection.redis.expire(self.ip, 60)
            return

        raise AttributeError
