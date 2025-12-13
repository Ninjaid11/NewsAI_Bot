import sqlite3
import hashlib
from typing import List, Dict, Optional
from datetime import datetime
from src.services.database.models import get_connection

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

    def exists(self, title: str, url: Optional[str], source: str) -> bool:
        """Проверяем, есть ли такая новость в БД"""
        guid = self._compute_guid(title, url, source)
        self._connect()
        try:
            self.cur.execute("""
                SELECT 1 FROM news
                WHERE title = ? AND source = ? AND source_url = ?
            """, (title, source, url))
            res = self.cur.fetchone()
        except sqlite3.OperationalError:
            self.cur.execute("SELECT 1 FROM news WHERE title = ? AND source = ?", (title, source))
            res = self.cur.fetchone()
        self._close()
        return bool(res)

    def save(self, item: Dict) -> int:
        self._connect()

        title = item.get("title")
        content = item.get("content")
        summary = item.get("summary")
        image_url = item.get("image_url")
        source = item.get("source")
        source_url = item.get("source_url")
        published_at = item.get("published_at")
        created_at = datetime.utcnow().isoformat()

        try:
            self.cur.execute("""
                INSERT INTO news (title, content, summary, image_url, source, source_url, published_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, content, summary, image_url, source, source_url, published_at, created_at))
            news_id = self.cur.lastrowid
        except Exception as e:
            print("Error saving news:", e)
            news_id = 0

        self._close()
        return news_id

    def get_latest(self, limit: int = 5) -> List[Dict]:
        self._connect()
        self.cur.execute("""
            SELECT id, title, content, summary, image_url, source, source_url, published_at, created_at
            FROM news
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = self.cur.fetchall()
        self._close()

        result = []
        for r in rows:
            result.append({
                "id": r[0],
                "title": r[1],
                "content": r[2],
                "summary": r[3],
                "image_url": r[4],
                "source": r[5],
                "source_url": r[6],
                "published_at": r[7],
                "created_at": r[8]
            })
        return result
