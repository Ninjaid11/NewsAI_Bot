import time

from src.services.database.news_repository import NewsRepository
from src.services.news.news_summarizer import NewsSummarizer
from src.services.llm.llm_service import LLMService

class BatchProcessor:
    def __init__(self, batch_size=5, pause_sec=2):
        self.batch_size = batch_size
        self.pause_sec = pause_sec
        self.new_repo = NewsRepository()
        self.llm = LLMService()
        self.summarizer = NewsSummarizer(self.llm)

    def get_news_to_process(self, limit=50):
        pass

    def generate_summary(self):
        pass

    def process_news_item(self):
        pass

    def run(self):
        pass