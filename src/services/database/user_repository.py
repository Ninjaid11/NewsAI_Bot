import json
from datetime import datetime
from src.services.database.models import get_connection

class UserRepository:
    """
    Репозиторий для работы с таблицей users.

    Отвечает за:
    - создание пользователя
    - хранение и изменение настроек (settings)
    - подписку / отписку
    - язык пользователя
    """

    def ensure_user(self, telegram_id: int, name: str):
        """
        Гарантирует, что пользователь существует в БД.
        Если пользователя нет — создаёт его с дефолтными настройками.
        """
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT 1 FROM users WHERE telegram_id = ?", (telegram_id,))
        exists = cur.fetchone()

        if not exists:
            default_settings = {
                "subscribed": True,
                "news_interval": 1,
                "lang": "en"
            }
            cur.execute(
                "INSERT INTO users (telegram_id, name, settings) VALUES (?, ?, ?)",
                (telegram_id, name, json.dumps(default_settings))
            )

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
        """
        Возвращает настройки пользователя в виде dict.
        """
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT settings FROM users WHERE telegram_id = ?",
            (telegram_id,)
        )
        row = cur.fetchone()
        conn.close()

        default_settings = {
            "subscribed": True,
            "news_interval": 1,
            "lang": "en"
        }

        if not row or not row[0]:
            return default_settings.copy()

        try:
            settings = json.loads(row[0])
        except json.JSONDecodeError:
            return default_settings.copy()

        for key, value in default_settings.items():
            settings.setdefault(key, value)

        return settings

    def update_settings(self, telegram_id: int, settings: dict):
        """
        Полностью перезаписывает settings пользователя в БД.
        """
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET settings = ? WHERE telegram_id = ?",
                    (json.dumps(settings), telegram_id))
        conn.commit()
        conn.close()

    def get_setting(self, telegram_id: int, key: str, default=None):
        """
        Возвращает одно конкретное значение настройки.
        """
        settings = self.get_settings(telegram_id)
        return settings.get(key, default)

    def set_setting(self, telegram_id: int, key: str, value):
        """
        Устанавливает одно конкретное значение настройки
        и сохраняет его в БД.
        """
        settings = self.get_settings(telegram_id)
        settings[key] = value
        self.update_settings(telegram_id, settings)