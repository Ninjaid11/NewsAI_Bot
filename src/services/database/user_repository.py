import json
from src.services.database.models import get_connection
from src.core.log_config import Logger

logger = Logger().get_logger()

DEFAULT_SETTINGS = {
    "subscribed": True,
    "send_times": ["morning"],
    "lang": "en"
}

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
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM users WHERE telegram_id = ?", (telegram_id,))
            exists = cur.fetchone()

            if not exists:
                cur.execute(
                    "INSERT INTO users (telegram_id, name, settings) VALUES (?, ?, ?)",
                    (telegram_id, name, json.dumps(DEFAULT_SETTINGS))
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Ошибка при ensure_user для telegram_id={telegram_id}: {e}")
        finally:
            if conn:
                conn.close()

    def unsubscribe(self, telegram_id: int):
        try:
            settings = self.get_settings(telegram_id)
            settings["subscribed"] = False
            self.update_settings(telegram_id, settings)
        except Exception as e:
            logger.error(f"Ошибка при отключении рассылки для telegram_id={telegram_id}: {e}")

    def subscribe(self, telegram_id: int):
        try:
            settings = self.get_settings(telegram_id)
            settings["subscribed"] = True
            self.update_settings(telegram_id, settings)
        except Exception as e:
            logger.error(f"Ошибка при включении рассылки для telegram_id={telegram_id}: {e}")

    def get_subscribed_users(self) -> list[int]:
        conn = None
        subscribed = []
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT telegram_id, settings FROM users")
            rows = cur.fetchall()

            for telegram_id, s in rows:
                try:
                    settings = json.loads(s) if s else {}
                    if settings.get("subscribed", False):
                        subscribed.append(telegram_id)
                except json.JSONDecodeError:
                    continue
        except Exception as e:
            logger.error(f"Ошибка при получении подписанных пользователей: {e}")
        finally:
            if conn:
                conn.close()
        return subscribed

    def get_settings(self, telegram_id: int) -> dict:
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT settings FROM users WHERE telegram_id = ?", (telegram_id,))
            row = cur.fetchone()

            settings = {}
            if row and row[0]:
                try:
                    settings = json.loads(row[0])
                except json.JSONDecodeError:
                    logger.warning(f"Неверный JSON в настройках telegram_id={telegram_id}")

            for key, value in DEFAULT_SETTINGS.items():
                settings.setdefault(key, value)

            return settings

        except Exception as e:
            logger.error(f"Ошибка при получении настроек для telegram_id={telegram_id}: {e}")
            return DEFAULT_SETTINGS.copy()
        finally:
            if conn:
                conn.close()

    def update_settings(self, telegram_id: int, settings: dict):
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("UPDATE users SET settings = ? WHERE telegram_id = ?",
                        (json.dumps(settings), telegram_id))
            conn.commit()
        except Exception as e:
            logger.error(f"Ошибка при обновлении настроек для telegram_id={telegram_id}: {e}")
        finally:
            if conn:
                conn.close()

    def get_setting(self, telegram_id: int, key: str, default=None):
        try:
            settings = self.get_settings(telegram_id)
            return settings.get(key, default)
        except Exception as e:
            logger.error(f"Ошибка при получении настройки '{key}' для telegram_id={telegram_id}: {e}")
            return default

    def set_setting(self, telegram_id: int, key: str, value):
        try:
            settings = self.get_settings(telegram_id)
            settings[key] = value
            self.update_settings(telegram_id, settings)
        except Exception as e:
            logger.error(f"Ошибка при установке настройки '{key}' для telegram_id={telegram_id}: {e}")