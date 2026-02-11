import time
from typing import List, Dict

from src.services.database.news_repository import NewsRepository
from src.services.news.news_summarizer import NewsSummarizer
from src.services.translator.google_translator import translate_to_ru

from src.core.log_config import Logger

logger = Logger().get_logger()

class SummaryBatchService:
    """Batch-процесс для генерации summary и перевода title_ru, без перезаписи существующих данных."""

    def __init__(
        self,
        news_repo: NewsRepository,
        summarizer: NewsSummarizer,
        batch_size: int = 5,
        pause_sec: int = 15
    ):
        self.news_repo = news_repo
        self.summarizer = summarizer
        self.batch_size = batch_size
        self.pause_sec = pause_sec

    def get_news_to_process(self) -> List[Dict]:
        """Получаем новости без summary"""
        try:
            news_list = self.news_repo.get_without_summary(self.batch_size)
            return news_list
        except Exception as e:
            logger.error(f"Ошибка при получении новостей: {e}")
            return []

    def process_news_item(self, news: Dict) -> None:
        """Обрабатывает одну новость, генерируя summary и перевод title_ru если нужно"""
        try:
            title_en = news.get("title", "<нет заголовка>")
            title_ru = news.get("title_ru") or ""
            content = news.get("content") or ""
            published_at = news.get("published_at") or ""
            summary_en = news.get("summary_en") or ""
            summary_ru = news.get("summary_ru") or ""

            if not title_ru:
                try:
                    title_ru = translate_to_ru(title_en)
                except Exception as e:
                    logger.error(f"Ошибка перевода title на русский для новости id={news.get('id')}: {e}")
                    title_ru = title_en

            if not summary_en:
                try:
                    summary_en = self.summarizer.summarize(
                        title=title_en,
                        content=content,
                        published_at=published_at,
                        lang="en"
                    )
                except Exception as e:
                    logger.error(f"Ошибка генерации summary_en для новости id={news.get('id')}: {e}")
                    summary_en = ""

            if not summary_ru:
                try:
                    summary_ru = self.summarizer.summarize(
                        title=title_ru,
                        content=content,
                        published_at=published_at,
                        lang="ru"
                    )
                except Exception as e:
                    logger.error(f"Ошибка генерации summary_ru для новости id={news.get('id')}: {e}")
                    summary_ru = ""

            self.news_repo.save_summary(
                news_id=news["id"],
                summary_en=summary_en or "",
                summary_ru=summary_ru or "",
                title_ru=title_ru
            )
        except Exception as e:
            logger.error(f"Ошибка при обработке новости '{news.get('title', '')[:60]}': {e}")

    def generate_summary(self, news_list: List[Dict]) -> None:
        """Обрабатывает список новостей с паузой между запросами"""
        for news in news_list:
            self.process_news_item(news)
            time.sleep(self.pause_sec)

    def run(self) -> None:
        """Точка входа batch-процесса"""
        logger.info("🚀 Batch стартовал")
        news_list = self.get_news_to_process()

        if not news_list:
            logger.info("Нет новостей для обработки")
            return

        self.generate_summary(news_list)
        logger.info("🎉 Batch успешно завершён")