import sqlite3
from typing import Optional
from contextlib import contextmanager
from .config import config


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def execute_query(self, query: str, params: tuple = ()):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def execute_query_one(self, query: str, params: tuple = ()):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()

    def execute_write(self, query: str, params: tuple = ()):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid

    def get_tables(self):
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        return self.execute_query(query)

    def get_table_schema(self, table_name: str):
        query = f"PRAGMA table_info({table_name})"
        return self.execute_query(query)


def get_database(source: str = "kilo") -> Database:
    db_path = config.get_db_path(source)
    return Database(db_path)


db_kilo = get_database("kilo")
db_opencode = get_database("opencode")


def get_db(source: str = "kilo") -> Database:
    if source == "opencode":
        return db_opencode
    return db_kilo
