
from peewee import *
from datetime import datetime
from os import path as op


db = SqliteDatabase(None)
DB_FILE = 'erika_data.db'
PROJECT_DIR = op.dirname(__file__)
DB_FILE_PATH = op.join(PROJECT_DIR, '', DB_FILE)


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


class Typewriter(Model):
    user_firstname = CharField(null = True)
    user_lastname = CharField(null = True)
    erika_name = CharField(null = True, unique=True)
    user_email = CharField(null = True)
    uuid = CharField(null = False, unique=True)
    email = CharField(null = True)
    created_at = DateTimeField(default=datetime.now)
    # Extra-Settings
    status = IntegerField(default=0)
    chat_active = BooleanField(default=1)
    last_seen = DateTimeField(default=datetime.now)

    class Meta:
        database = db


class Message(Model):
    typewriter = ForeignKeyField(Typewriter, related_name='messages')
    sender = CharField()
    subject = CharField()
    body = TextField()
    received_at = DateTimeField(default=datetime.now)

    class Meta:
        database = db

def initialize_models():
    db.init(DB_FILE_PATH)


if __name__ == '__main__':
    tables = [Textdata, Typewriter, Message]
    db.init(DB_FILE_PATH)
    print(f"Creating Tables {tables}... in {DB_FILE_PATH}")
    db.create_tables(tables)
