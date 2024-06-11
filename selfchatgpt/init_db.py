import sqlite3
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Initialize the database tables'

    def handle(self, *args, **kwargs):
        path = './db_chatlog/db_chatlog.db'
        conn = sqlite3.connect(path)

        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY,
            datetime TEXT NOT NULL,
            query TEXT NOT NULL,
            sim1 REAL,
            sim2 REAL,
            sim3 REAL,
            answer TEXT
        )
        ''')

        conn.commit()
        conn.close()
        self.stdout.write(self.style.SUCCESS('Database initialized successfully'))
