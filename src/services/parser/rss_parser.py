import feedparser
from email.utils import parsedate_to_datetime
from src.services.database.news_repository import NewsRepository

class RSSParser:
    """
    Парсер RSS-лент новостей.
    Загружает новости из указанных источников, проверяет дубликаты
    и сохраняет новые записи в базу данных.
    """
    FALLBACK_IMAGE = "static/fallback.jpg"

    def __init__(self, rss_list: list[str], news_repo: NewsRepository):
        self.rss_list = rss_list
        self.news_repo = news_repo

    async def fetch_all(self) -> int:
        total_news = 0
        for url in self.rss_list:
            total_news += await self._parse_feed(url)
        return total_news

    async def _parse_feed(self, url: str) -> int:
        feed = feedparser.parse(url)
        count = 0

        for item in feed.entries:
            title = item.get("title", "")
            link = item.get("link", "")
            published_raw = item.get("published")
            published_at = parsedate_to_datetime(published_raw).isoformat() if published_raw else None
            content = item.get("description", "")
            image_url = self._extract_image(item)

            if self.news_repo.exists(title, link, url):
                continue

            self.news_repo.save({
                "title": title,
                "content": content,
                "image_url": image_url,
                "source": url,
                "source_url": link,
                "published_at": published_at
            })

            count += 1

        return count

    def _extract_image(self, item) -> str:
        if "media_thumbnail" in item:
            thumbs = item.media_thumbnail
            if thumbs and "url" in thumbs[0]:
                return thumbs[0]["url"]
        return self.FALLBACK_IMAGE