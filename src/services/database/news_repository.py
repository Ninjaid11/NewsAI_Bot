import sqlite3
import hashlib
from typing import List, Dict, Optional
from datetime import datetime
from src.services.database.models import get_connection
from src.core.log_config import Logger

logger = Logger().get_logger()


class NewsRepository:
    """
    Класс для работы с таблицей news.
    Реализует базовые операции: добавление, проверка дубликатов, получение последних новостей.
    """
    def __init__(self):
        self.conn = None
        self.cur = None

    def _connect(self):
        self.conn = get_connection()
        self.cur = self.conn.cursor()

    def _close(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()
            self.conn = None
            self.cur = None

    def _compute_guid(self, title: str, url: Optional[str], source: str) -> str:
        key = (url or title) + "|" + source
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    def exists(self, title_en: str, url: Optional[str], source: str) -> bool:
        """Проверяем, есть ли такая новость в БД"""
        self._connect()
        try:
            self.cur.execute("""
                SELECT 1 FROM news
                WHERE source = ? AND source_url = ?
                LIMIT 1
            """, (source, url))
            res = self.cur.fetchone()
            return bool(res)
        except Exception as e:
            logger.error(f"Ошибка проверки существования новости (source={source}, url={url}): {e}")
            return False
        finally:
            self._close()

    def save(self, item: Dict) -> int:
        self._connect()
        news_id = 0
        try:
            title_en = item.get("title_en", "")
            title_ru = item.get("title_ru", "")
            content = item.get("content")
            image_url = item.get("image_url")
            source = item.get("source")
            source_url = item.get("source_url")
            published_at = item.get("published_at")
            created_at = datetime.utcnow().isoformat()

            self.cur.execute("""
                INSERT INTO news 
                (title_en, title_ru, content, image_url, source, source_url, published_at, created_at, summary_en, summary_ru)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (title_en, title_ru, content, image_url, source, source_url, published_at, created_at, "", ""))
            news_id = self.cur.lastrowid
        except Exception as e:
            logger.error(f"Ошибка при сохранении новости (source={item.get('source')}): {e}")
        finally:
            self._close()
        return news_id

    def get_latest(self, limit: int = 5) -> List[Dict]:
        self._connect()
        result = []
        try:
            self.cur.execute("""
                SELECT id, title_en, title_ru, content, summary_en, summary_ru, image_url, source, source_url, published_at, created_at
                FROM news
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            rows = self.cur.fetchall()
            for r in rows:
                result.append({
                    "id": r[0],
                    "title_en": r[1],
                    "title_ru": r[2],
                    "content": r[3],
                    "summary_en": r[4],
                    "summary_ru": r[5],
                    "image_url": r[6],
                    "source": r[7],
                    "source_url": r[8],
                    "published_at": r[9],
                    "created_at": r[10]
                })
        except Exception as e:
            logger.error(f"Ошибка при получении последних новостей: {e}")
        finally:
            self._close()
        return result

    def save_summary(self, news_id: int, summary_en: str, summary_ru: str, title_ru: str = ""):
        self._connect()
        try:
            self.cur.execute("""
                UPDATE news
                SET summary_en = ?, summary_ru = ?, title_ru = ?
                WHERE id = ?
            """, (summary_en, summary_ru, title_ru, news_id))
        except Exception as e:
            logger.error(f"Ошибка при сохранении summary для новости id={news_id}: {e}")
        finally:
            self._close()

    def get_without_summary(self, limit: int = 10):
        self._connect()
        result = []
        try:
            self.cur.execute("""
                SELECT id, title_en, title_ru, content, published_at
                FROM news
                WHERE summary_en = '' OR summary_en IS NULL
                ORDER BY id ASC
                LIMIT ?
            """, (limit,))
            rows = self.cur.fetchall()
            result = [
                {
                    "id": r[0],
                    "title_en": r[1],
                    "title_ru": r[2],
                    "content": r[3],
                    "published_at": r[4],
                }
                for r in rows
            ]
        except Exception as e:
            logger.error(f"Ошибка при получении новостей без summary: {e}")
        finally:
            self._close()
        return result