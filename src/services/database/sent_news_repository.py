from src.services.database.models import get_connection
from datetime import datetime

class SentNewsRepository:
    """
    Класс для работы с таблицей sent_news.
    Хранит информацию о новостях, которые уже были отправлены пользователям,
    и позволяет предотвращать повторную отправку.
    """
    def was_sent(self, user_id: int, news_id: int) -> bool:
        # проверяет
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT 1 FROM sent_news
            WHERE user_id = ? AND news_id = ?
        """, (user_id, news_id))

        res = cur.fetchone()
        conn.close()

        return bool(res)

    def mark_sent(self, user_id: int, news_id: int):
        # вызывается ПОСЛЕ успешной отправки сообщения
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO sent_news (user_id, news_id, sent_at)
            VALUES (?, ?, ?)
        """, (user_id, news_id, datetime.utcnow().isoformat()))

        conn.commit()
        conn.close()