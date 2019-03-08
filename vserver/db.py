from peewee import Model, CharField, IntegerField
from playhouse.postgres_ext import BinaryJSONField, ArrayField

from vserver.connection import connection



class BaseModel(Model):
    class Meta:
        database = connection.db


class WorkerDBMixin(BaseModel):
    ip = CharField()
    login = CharField()
    password = CharField()
    port = IntegerField()
    info = BinaryJSONField()
    accounts = ArrayField()
    proxies = ArrayField()

    class Meta:
        table_name = 'server.worker'
        indexes = (
            (('ip', 'port'), True),
        )
