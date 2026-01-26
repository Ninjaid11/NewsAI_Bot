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

        title = news_item["title"]
        content = news_item["content"]
        image_url = news_item.get("image_url") or self.FALLBACK_IMAGE

        summary_en = news_item.get("summary_en")
        summary_ru = news_item.get("summary_ru")

        if lang == "ru":
            if not summary_ru:
                summary_ru = self.summarizer.summarize(
                    title=title,
                    content=content,
                    published_at=published_at,
                    lang="ru"
                )
        else:
            if not summary_en:
                summary_en = self.summarizer.summarize(
                    title=title,
                    content=content,
                    published_at=published_at,
                    lang="en"
                )

        self.news_repo.save_summary(
            news_item["id"],
            summary_en or "",
            summary_ru or ""
        )

        summary = summary_ru if lang == "ru" else summary_en

        return {
            "id": news_item["id"],
            "title": title,
            "published_at": published_at,
            "summary": summary,
            "image_url": image_url,
            "source_url": news_item.get("source_url")
        }
