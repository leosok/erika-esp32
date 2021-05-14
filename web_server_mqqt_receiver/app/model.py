
from peewee import *
from datetime import datetime


db = SqliteDatabase(None)


class Textdata(Model):
    content = TextField()
    timestamp = DateTimeField(default=datetime.now)
    hashid = CharField()

    class Meta:
        database = db

    @classmethod
    def count_lines(cls, hashid):
        result = cls.select().where(cls.hashid == hashid).count()
        return result



def initialize_models():
    db.init('erika_text_data.db')
    # Unique constraint will take care of MQQT qos level 1, which can send msgs more than once
    Textdata.add_index(Textdata.hashid, Textdata.content, unique=True)
    db.create_tables([Textdata])