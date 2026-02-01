import time
from typing import List, Dict

from src.services.database.news_repository import NewsRepository
from src.services.news.news_summarizer import NewsSummarizer
from src.core.log_config import Logger

logger = Logger().get_logger()

class SummaryBatchService:
    def __init__(
        self,
        news_repo: NewsRepository,
        summarizer: NewsSummarizer,
        batch_size: int = 5,
        pause_sec: int = 2
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
        """Обрабатывает одну новость"""
        try:
            summary_en = self.summarizer.summarize(
                title=news["title"],
                content=news["content"],
                published_at=news["published_at"],
                lang="en"
            )
            summary_ru = self.summarizer.summarize(
                title=news["title"],
                content=news["content"],
                published_at=news["published_at"],
                lang="ru"
            )
            self.news_repo.save_summary(
                news["id"],
                summary_en or "",
                summary_ru or ""
            )
        except Exception as e:
            logger.error(f"Ошибка при обработке новости '{news['title'][:60]}': {e}")

    def generate_summary(self, news_list: List[Dict]) -> None:
        """Генерирует summary для списка новостей"""
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