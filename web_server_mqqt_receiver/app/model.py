
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

    
    @classmethod
    def as_fulltext(cls, hashid, min_length=30):
        '''
        Everything < min_length will be put in a seperate line
        '''
        lines = cls.select().where(cls.hashid==hashid).order_by(cls.line_number)
        fulltext = ''
        for line in lines:
            if len(line.content) <= min_length:
                fulltext += line.content + '\n'
            else:
                fulltext += line.content + ' '
        return fulltext
        


def initialize_models():

    db.init(op.join(PROJECT_DIR,'..','erika_text_data.db'))
    # Unique constraint will take care of MQQT qos level 1, which can send msgs more than once
    Textdata.add_index(Textdata.hashid, Textdata.content, unique=True)
    db.create_tables([Textdata])