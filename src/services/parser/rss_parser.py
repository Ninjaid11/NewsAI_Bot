import feedparser
from datetime import datetime
from src.services.database.news_repository import NewsRepository
from src.services.llm.service import LLMService


class RSSParser:
    def __init__(self, rss_list: list[str], llm: LLMService, db: NewsRepository):
        self.rss_list = rss_list
        self.llm = llm
        self.db = db

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
            link = item.get("link")
            content = item.get("summary") or item.get("description")
            date = item.get("published", datetime.now().isoformat())

            if self.db.exists(title, link, url):
                continue

            summary = await self.llm.summarize(content)

            self.db.save({
                "title": title,
                "content": content,
                "summary": summary,
                "image_url": None,
                "source": url,
                "source_url": link,
                "published_at": date,
            })
            count += 1

        return count