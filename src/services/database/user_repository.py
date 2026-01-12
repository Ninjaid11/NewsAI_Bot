import json
from datetime import datetime
from src.services.database.models import get_connection

class UserRepository:
    """
    Работа с таблицей users.
    Реализует создание/обновление пользователя и хранение настроек рассылки
    (подписка, лимит новостей, интервал, время последней рассылки).
    """

    def add_or_update(self, telegram_id: int, name: str):
        default_settings = {
            "subscribed": True,      # активная подписка по умолчанию
            "news_limit": 1,         # количество новостей за раз
            "news_interval": 1,      # интервал рассылки в часах
            "last_sent": None        # время последней отправки
        }

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (telegram_id, name, settings)
            VALUES (?, ?, ?)
            ON CONFLICT(telegram_id)
            DO UPDATE SET name = excluded.name
        """, (telegram_id, name, json.dumps(default_settings)))
        conn.commit()
        conn.close()

    def unsubscribe(self, telegram_id: int):
        """Отключить рассылку для пользователя"""
        settings = self.get_settings(telegram_id)
        settings["subscribed"] = False
        self.update_settings(telegram_id, settings)

    def subscribe(self, telegram_id: int):
        """Включить рассылку для пользователя"""
        settings = self.get_settings(telegram_id)
        settings["subscribed"] = True
        self.update_settings(telegram_id, settings)

    def get_subscribed_users(self) -> list[int]:
        """Получить список ID пользователей с активной подпиской"""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT telegram_id, settings FROM users")
        rows = cur.fetchall()
        conn.close()

        subscribed = []
        for telegram_id, s in rows:
            try:
                settings = json.loads(s) if s else {}
                if settings.get("subscribed", False):
                    subscribed.append(telegram_id)
            except json.JSONDecodeError:
                continue
        return subscribed

    def get_settings(self, telegram_id: int) -> dict:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT settings FROM users WHERE telegram_id = ?", (telegram_id,))
        row = cur.fetchone()
        conn.close()
        return json.loads(row[0]) if row and row[0] else {}

    def update_settings(self, telegram_id: int, settings: dict):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET settings = ? WHERE telegram_id = ?",
                    (json.dumps(settings), telegram_id))
        conn.commit()
        conn.close()

    def get_setting(self, telegram_id: int, key: str, default=None):
        settings = self.get_settings(telegram_id)
        return settings.get(key, default)

    def set_setting(self, telegram_id: int, key: str, value):
        settings = self.get_settings(telegram_id)
        settings[key] = value
        self.update_settings(telegram_id, settings)