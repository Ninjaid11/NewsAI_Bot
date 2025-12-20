import json
from src.services.database.models import get_connection

class UserRepository:
    """
    Класс для работы с таблицей users.
    Реализует операции создания пользователей, подписки и отписки от рассылки,
    а также получения списка подписанных пользователей.
    """
    def add_or_update(self, telegram_id: int, name: str):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
                    INSERT INTO users (telegram_id, name, settings, subscribed)
                    VALUES (?, ?, ?, 1)
                    ON CONFLICT(telegram_id)
                    DO UPDATE SET subscribed = 1
                """, (
            telegram_id,
            name,
            json.dumps({"news_limit": 5})
        ))

        conn.commit()
        conn.close()

    def unsubscribe(self, telegram_id: int):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
                    UPDATE users
                    SET subscribed = 0
                    WHERE telegram_id = ?
                """, (telegram_id,))

        conn.commit()
        conn.close()

    def get_subscribed_users(self) -> list[int]:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT telegram_id
            FROM users
            WHERE subscribed = 1
        """)

        rows = cur.fetchall()
        conn.close()

        return [r[0] for r in rows]

    def get_settings(self, telegram_id: int) -> dict:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
                    SELECT settings FROM users
                    WHERE telegram_id = ?
                """, (telegram_id,))

        row = cur.fetchone()
        conn.close()

        return json.loads(row[0]) if row and row[0] else {}

    def update_settings(self, telegram_id: int, settings: dict):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE users
            SET settings = ?
            WHERE telegram_id = ?
        """, (json.dumps(settings), telegram_id))

        conn.commit()
        conn.close()