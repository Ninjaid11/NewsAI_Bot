import json
from datetime import datetime
from src.services.database.models import get_connection
from src.core.log_config import Logger

logger = Logger().get_logger()


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
        except Exception as e:
            logger.error(f"Ошибка при ensure_user для telegram_id={telegram_id}: {e}")
        finally:
            if conn:
                conn.close()

    def unsubscribe(self, telegram_id: int):
        """Отключить рассылку для пользователя"""
        try:
            settings = self.get_settings(telegram_id)
            settings["subscribed"] = False
            self.update_settings(telegram_id, settings)
        except Exception as e:
            logger.error(f"Ошибка при отключении рассылки для telegram_id={telegram_id}: {e}")

    def subscribe(self, telegram_id: int):
        """Включить рассылку для пользователя"""
        try:
            settings = self.get_settings(telegram_id)
            settings["subscribed"] = True
            self.update_settings(telegram_id, settings)
        except Exception as e:
            logger.error(f"Ошибка при включении рассылки для telegram_id={telegram_id}: {e}")

    def get_subscribed_users(self) -> list[int]:
        """Получить список ID пользователей с активной подпиской"""
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
        """
        Возвращает настройки пользователя в виде dict.
        """
        conn = None
        default_settings = {
            "subscribed": True,
            "news_interval": 1,
            "lang": "en"
        }

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT settings FROM users WHERE telegram_id = ?", (telegram_id,))
            row = cur.fetchone()

            if not row or not row[0]:
                return default_settings.copy()

            try:
                settings = json.loads(row[0])
            except json.JSONDecodeError:
                logger.warning(f"Неверный JSON в настройках telegram_id={telegram_id}")
                return default_settings.copy()

            for key, value in default_settings.items():
                settings.setdefault(key, value)

            return settings

        except Exception as e:
            logger.error(f"Ошибка при получении настроек для telegram_id={telegram_id}: {e}")
            return default_settings.copy()
        finally:
            if conn:
                conn.close()

    def update_settings(self, telegram_id: int, settings: dict):
        """
        Полностью перезаписывает settings пользователя в БД.
        """
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
        """
        Возвращает одно конкретное значение настройки.
        """
        try:
            settings = self.get_settings(telegram_id)
            return settings.get(key, default)
        except Exception as e:
            logger.error(f"Ошибка при получении настройки '{key}' для telegram_id={telegram_id}: {e}")
            return default

    def set_setting(self, telegram_id: int, key: str, value):
        """
        Устанавливает одно конкретное значение настройки
        и сохраняет его в БД.
        """
        try:
            settings = self.get_settings(telegram_id)
            settings[key] = value
            self.update_settings(telegram_id, settings)
        except Exception as e:
            logger.error(f"Ошибка при установке настройки '{key}' для telegram_id={telegram_id}: {e}")