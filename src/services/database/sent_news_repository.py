from src.services.database.models import get_connection
from datetime import datetime
from src.core.log_config import Logger

logger = Logger().get_logger()


class SentNewsRepository:
    """
    Класс для работы с таблицей sent_news.
    Хранит информацию о новостях, которые уже были отправлены пользователям,
    и позволяет предотвращать повторную отправку.
    """
    def was_sent(self, user_id: int, news_id: int) -> bool:
        """Проверяет, была ли новость отправлена пользователю"""
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT 1 FROM sent_news
                WHERE user_id = ? AND news_id = ?
            """, (user_id, news_id))
            res = cur.fetchone()
            return bool(res)
        except Exception as e:
            logger.error(f"Ошибка проверки отправки новости (user_id={user_id}, news_id={news_id}): {e}")
            return False
        finally:
            if conn:
                conn.close()

    def mark_sent(self, user_id: int, news_id: int):
        """Отмечает новость как отправленную пользователю"""
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO sent_news (user_id, news_id, sent_at)
                VALUES (?, ?, ?)
            """, (user_id, news_id, datetime.utcnow().isoformat()))
            conn.commit()
        except Exception as e:
            logger.error(f"Ошибка при отметке новости как отправленной (user_id={user_id}, news_id={news_id}): {e}")
        finally:
            if conn:
                conn.close()