
from peewee import *


db = SqliteDatabase(None)


class Textdata(Model):
    content = TextField()
    timestamp = DateTimeField(default=datetime.datetime.now)
    hashid = CharField()

    class Meta:
        database = db


def initialize():
    db.init('erika_text_data.db')
    # Unique constraint will take care of MQQT qos level 1, which can send msgs more than once
    Textdata.add_index(Textdata.hashid, Textdata.content, unique=True)
    db.create_tables([Textdata])