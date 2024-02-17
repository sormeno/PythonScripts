import sqlite3

class DB:
    def __init__(self, db_file):
        self.db_file = db_file

    def execute_query(self, query, data=()):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(query, data)
        result = cursor.fetchall()
        conn.commit()
        conn.close()
        return result