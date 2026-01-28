import time

from src.services.database.news_repository import NewsRepository
from src.services.news.news_summarizer import NewsSummarizer

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

    def get_news_to_process(self):
        """
        Получаем новости без summary
        """
        return self.news_repo.get_without_summary(self.batch_size)

    def process_news_item(self, news: dict):
        """
        Обрабатывает одну новость
        """
        print(f"🧠 Генерация summary: {news['title'][:60]}")

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

        print("  ✅ summary сохранён")

    def generate_summary(self, news_list: list[dict]):
        """
        Генерирует summary для списка новостей
        """
        for news in news_list:
            self.process_news_item(news)
            time.sleep(self.pause_sec)

    def run(self):
        """
        Точка входа batch-процесса
        """
        news_list = self.get_news_to_process()

        if not news_list:
            print("✅ Нет новостей для обработки")
            return

        print(f"🚀 Batch стартовал, новостей: {len(news_list)}")

        self.generate_summary(news_list)

        print("🎉 Batch успешно завершён")