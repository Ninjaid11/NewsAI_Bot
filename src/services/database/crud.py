from connection import get_connection

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Пользователи
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            name TEXT,
            settings TEXT,
            subscribed BOOLEAN
        )
    """)

    # Новости
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS news (
            news_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            summary TEXT,
            image TEXT,
            source TEXT,
            date TEXT
        )
    """)

    # Отправленные новости
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sent_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            news_id INTEGER,
            sent_at TEXT
        )
    """)

    conn.commit()
    conn.close()