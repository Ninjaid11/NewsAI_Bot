from datetime import datetime
from src.services.news.news_summarizer import NewsSummarizer
from src.services.database.news_repository import NewsRepository

class NewsProcessor:
    """
    Класс для обработки одной новости перед отправкой пользователю.
    Обрабатывает дату, картинку и генерирует summary через LLM.
    Сохраняет summary_en и summary_ru в БД.
    """
    FALLBACK_IMAGE = "static/fallback.jpg"

    def __init__(self, summarizer: NewsSummarizer, news_repo: NewsRepository):
        self.summarizer = summarizer
        self.news_repo = news_repo

    def process(self, news_item: dict, lang: str = "en") -> dict:
        published_at = news_item.get("published_at", "")
        if published_at:
            try:
                dt = datetime.fromisoformat(published_at)
                published_at = dt.strftime("%d %B %Y, %H:%M")
            except Exception:
                pass

        image_url = news_item.get("image_url") or self.FALLBACK_IMAGE
        title = news_item.get("title", "")
        content = news_item.get("content", "")

        news_id = self.news_repo.save({
            "title": title,
            "content": content,
            "image_url": image_url,
            "source": news_item.get("source"),
            "source_url": news_item.get("source_url"),
            "published_at": published_at
        })

        summary_en = self.summarizer.summarize(title=title, content=content, published_at=published_at, lang="en")
        summary_ru = self.summarizer.summarize(title=title, content=content, published_at=published_at, lang="ru")

        # сохраняем summary в БД
        self.news_repo.save_summary(news_id, summary_en, summary_ru)

        summary = summary_ru if lang == "ru" else summary_en

        return {
            "id": news_id,
            "title": title,
            "published_at": published_at,
            "summary": summary,
            "image_url": image_url,
            "source_url": news_item.get("source_url")
        }
