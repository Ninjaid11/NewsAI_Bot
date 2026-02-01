import sqlite3

DB_NAME = "news_ai.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

class Database:
    """
    Класс инициализации базы данных.
    Создаёт таблицы и отвечает за структуру базы данных приложения.
    """
    def __init__(self):
        self.conn = get_connection()
        self.cur = self.conn.cursor()

    def create_tables(self):
        self._create_users()
        self._create_news()
        self._create_sent_news()
        self.conn.commit()

    def _create_users(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                name TEXT,
                settings TEXT
            )
        """)

    def _create_news(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title_en TEXT,
                title_ru TEXT,
                content TEXT,
                summary_en TEXT DEFAULT '',
                summary_ru TEXT DEFAULT '',
                image_url TEXT,
                source TEXT,
                source_url TEXT,
                published_at TEXT,
                created_at TEXT
            )
        """)

    def _create_sent_news(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS sent_news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                news_id INTEGER,
                sent_at TEXT
            )
        """)

    def close(self):
        self.conn.close()
