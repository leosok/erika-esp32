from playhouse.migrate import *
from erika_cloud.models import DB_FILE_PATH
from datetime import datetime

db = SqliteDatabase(DB_FILE_PATH)
migrator = SqliteMigrator(db)

def add_last_seen():
    last_seen_field = DateTimeField(default=datetime.now)
    migrate(
        migrator.add_column('typewriter', 'last_seen', last_seen_field)
    )

if __name__ == '__main__':

    migrations = [
        "add_last_seen",
        "migrate(migrator.add_index('typewriter', ('uuid', ), unique=True))",
        "migrate(migrator.add_index('typewriter', ('erika_name', ), unique=True))"
    ]

    for m in migrations:
        try:
            eval(m + '()')
            print("OK: function `" + m + "` successfull.")
        except Exception as e:
            print("ERROR: " + str(e))