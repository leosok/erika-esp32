
from peewee import *
from datetime import datetime
from os import path as op


db = SqliteDatabase(None)
PROJECT_DIR = op.dirname(__file__)


class Textdata(Model):
    content = TextField()
    timestamp = DateTimeField(default=datetime.now)
    hashid = CharField()
    line_number = IntegerField()

    class Meta:
        database = db

    @classmethod
    def count_lines(cls, hashid):
        result = cls.select().where(cls.hashid == hashid).count()
        return result



def initialize_models():

    db.init(op.join(PROJECT_DIR,'..','erika_text_data.db'))
    # Unique constraint will take care of MQQT qos level 1, which can send msgs more than once
    Textdata.add_index(Textdata.hashid, Textdata.content, unique=True)
    db.create_tables([Textdata])