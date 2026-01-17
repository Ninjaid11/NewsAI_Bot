import feedparser
from email.utils import parsedate_to_datetime

from src.services.database.news_repository import NewsRepository
from src.services.llm.service import LLMService

class RSSParser:
    """
    Парсер RSS-лент новостей.
    Загружает новости из указанных источников, проверяет их на дубликаты
    и сохраняет новые записи в базу данных.
    """
    def __init__(self, rss_list: list[str], llm: LLMService, db: NewsRepository):
        self.rss_list = rss_list
        self.llm = llm
        self.db = db
        self.FALLBACK_IMAGE = "static/fallback.jpg"

    async def fetch_all(self):
        """Парсит все RSS-каналы"""
        total_news = 0

        for url in self.rss_list:
            total_news += await self._parse_signal(url)

    async def _parse_signal(self, url: str):
        """Парсит один RSS"""
        feed = feedparser.parse(url)
        count = 0

        for item in feed.entries:
            title = item.title
            date = parsedate_to_datetime(item.get("published"))
            image_url = self._extract_image(item)
            content = item.get("description")
            link = item.get("link")


            if self.db.exists(title, link, url):
                continue

            summary = await self.llm.summarize(content)

            self.db.save({
                "title": title,
                "content": content,
                "summary": summary,
                "image_url": image_url,
                "source": url,
                "source_url": link,
                "published_at": date,
            })
            count += 1

        return count

    def _extract_image(self, item) -> str | None:
        if "media_thumbnail" in item:
            thumbs = item.media_thumbnail
            if thumbs and "url" in thumbs[0]:
                return thumbs[0]["url"]
        return self.FALLBACK_IMAGE