from datetime import datetime
from src.services.news.news_summarizer import NewsSummarizer
from src.services.database.news_repository import NewsRepository
from src.services.translator.google_translator import translate_to_ru
from src.core.log_config import Logger

logger = Logger().get_logger()

class NewsProcessor:
    """
    Обрабатывает одну новость перед отправкой пользователю.
    Генерирует summary и переводит title на русский при необходимости.
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
            except Exception as e:
                logger.warning(f"Не удалось форматировать дату '{published_at}' для новости id={news_item.get('id')}: {e}")

        title_en = news_item.get("title_en", "")
        title_ru = news_item.get("title_ru", "")
        content = news_item.get("content") or ""
        image_url = news_item.get("image_url") or self.FALLBACK_IMAGE

        summary_en = news_item.get("summary_en")
        summary_ru = news_item.get("summary_ru")

        try:
            if lang == "ru":
                if not title_ru:
                    try:
                        title_ru = translate_to_ru(title_en)
                    except Exception as e:
                        logger.error(f"Ошибка перевода title на русский для новости id={news_item.get('id')}: {e}")
                        title_ru = title_en
                if not summary_ru:
                    try:
                        summary_ru = self.summarizer.summarize(
                            title=title_en,
                            content=content,
                            published_at=published_at,
                            lang="ru"
                        )
                    except Exception as e:
                        logger.error(f"Ошибка генерации summary_ru для новости id={news_item.get('id')}: {e}")
                        summary_ru = ""
            else:
                if not summary_en:
                    try:
                        summary_en = self.summarizer.summarize(
                            title=title_en,
                            content=content,
                            published_at=published_at,
                            lang="en"
                        )
                    except Exception as e:
                        logger.error(f"Ошибка генерации summary_en для новости id={news_item.get('id')}: {e}")
                        summary_en = ""
        except Exception as e:
            logger.error(f"Общая ошибка обработки новости id={news_item.get('id')}: {e}")

        try:
            self.news_repo.save_summary(
                news_item["id"],
                summary_en or "",
                summary_ru or "",
                title_ru=title_ru
            )
        except Exception as e:
            logger.error(f"Ошибка сохранения summary для новости id={news_item.get('id')}: {e}")

        summary = summary_ru if lang == "ru" else summary_en
        title = title_ru if lang == "ru" else title_en

        return {
            "id": news_item["id"],
            "title": title,
            "published_at": published_at,
            "summary": summary,
            "image_url": image_url,
            "source_url": news_item.get("source_url")
        }
