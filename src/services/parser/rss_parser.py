import feedparser
from email.utils import parsedate_to_datetime
from src.services.database.news_repository import NewsRepository
from src.services.translator.google_translator import translate_to_ru
from src.core.log_config import Logger

logger = Logger().get_logger()

class RSSParser:
    FALLBACK_IMAGE = "static/fallback.jpg"

    def __init__(self, rss_list: list[str], news_repo: NewsRepository):
        self.rss_list = rss_list
        self.news_repo = news_repo

    async def fetch_all(self) -> int:
        total_news = 0
        for url in self.rss_list:
            try:
                count = await self._parse_feed(url)
                total_news += count
            except Exception as e:
                logger.error(f"Ошибка обработки RSS feed '{url}': {e}")
        return total_news

    async def _parse_feed(self, url: str) -> int:
        try:
            feed = feedparser.parse(url)
        except Exception as e:
            logger.error(f"Ошибка парсинга RSS '{url}': {e}")
            return 0

        count = 0
        for item in feed.entries:
            try:
                title_en = item.get("title", "")
                source_url = item.get("link", "")

                # проверка на дубликат
                if self.news_repo.exists(title_en, source_url, url):
                    continue

                try:
                    title_ru = await translate_to_ru(title_en)
                except Exception as e:
                    logger.error(f"Ошибка перевода title на русский: '{title_en[:30]}...': {e}")
                    title_ru = title_en

                content = item.get("description", "")
                published_raw = item.get("published")
                try:
                    published_at = (
                        parsedate_to_datetime(published_raw).isoformat()
                        if published_raw else None
                    )
                except Exception as e:
                    logger.warning(f"Не удалось распарсить дату '{published_raw}': {e}")
                    published_at = None

                image_url = self._extract_image(item)

                try:
                    self.news_repo.save({
                        "title_en": title_en,
                        "title_ru": title_ru,
                        "content": content,
                        "image_url": image_url,
                        "source": url,
                        "source_url": source_url,
                        "published_at": published_at
                    })
                    count += 1
                except Exception as e:
                    logger.error(f"Ошибка сохранения новости '{title_en[:30]}...' из RSS '{url}': {e}")
            except Exception as e:
                logger.error(f"Ошибка обработки записи RSS '{url}': {e}")
        return count

    def _extract_image(self, item) -> str:
        try:
            if "media_thumbnail" in item:
                thumbs = item.media_thumbnail
                if thumbs and "url" in thumbs[0]:
                    return thumbs[0]["url"]
        except Exception as e:
            logger.warning(f"Ошибка извлечения изображения: {e}")
        return self.FALLBACK_IMAGE