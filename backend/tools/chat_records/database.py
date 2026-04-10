import sqlite3
import os
from contextlib import contextmanager


DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "workbench.db",
)


class Database:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._ensure_tables()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
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

    def execute_many(self, query: str, params_list: list):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount

    def _ensure_tables(self):
        with self.get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS chat_contact (
                    id TEXT PRIMARY KEY,
                    platform TEXT NOT NULL,
                    name TEXT,
                    alias TEXT,
                    remark TEXT,
                    type TEXT NOT NULL DEFAULT 'user',
                    avatar_url TEXT,
                    extra_json TEXT,
                    created_at INTEGER,
                    updated_at INTEGER
                );

                CREATE TABLE IF NOT EXISTS chat_conversation (
                    id TEXT PRIMARY KEY,
                    platform TEXT NOT NULL,
                    contact_id TEXT,
                    title TEXT,
                    last_message_time INTEGER,
                    message_count INTEGER DEFAULT 0,
                    extra_json TEXT,
                    created_at INTEGER,
                    updated_at INTEGER
                );

                CREATE TABLE IF NOT EXISTS chat_message (
                    id TEXT PRIMARY KEY,
                    platform TEXT NOT NULL,
                    conversation_id TEXT NOT NULL,
                    sender_id TEXT,
                    sender_name TEXT,
                    content TEXT,
                    msg_type TEXT NOT NULL DEFAULT 'text',
                    timestamp INTEGER NOT NULL,
                    extra_json TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_chat_contact_platform ON chat_contact(platform);
                CREATE INDEX IF NOT EXISTS idx_chat_conversation_platform ON chat_conversation(platform);
                CREATE INDEX IF NOT EXISTS idx_chat_conversation_contact ON chat_conversation(contact_id);
                CREATE INDEX IF NOT EXISTS idx_chat_message_platform ON chat_message(platform);
                CREATE INDEX IF NOT EXISTS idx_chat_message_conversation ON chat_message(conversation_id);
                CREATE INDEX IF NOT EXISTS idx_chat_message_timestamp ON chat_message(timestamp);
                CREATE INDEX IF NOT EXISTS idx_chat_message_sender ON chat_message(sender_id);

                CREATE VIRTUAL TABLE IF NOT EXISTS chat_message_fts USING fts5(
                    content,
                    sender_name,
                    content='chat_message',
                    content_rowid='rowid'
                );

                CREATE TRIGGER IF NOT EXISTS chat_message_ai AFTER INSERT ON chat_message BEGIN
                    INSERT INTO chat_message_fts(rowid, content, sender_name)
                    VALUES (new.rowid, new.content, new.sender_name);
                END;

                CREATE TRIGGER IF NOT EXISTS chat_message_ad AFTER DELETE ON chat_message BEGIN
                    INSERT INTO chat_message_fts(chat_message_fts, rowid, content, sender_name)
                    VALUES ('delete', old.rowid, old.content, old.sender_name);
                END;
            """)
            conn.commit()


db = Database()
