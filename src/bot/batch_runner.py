from src.services.database.news_repository import NewsRepository
from src.services.news.news_summarizer import NewsSummarizer
from src.services.llm.llm_service import LLMService

from src.batch.summary_batch import SummaryBatchService

def main():
    news_repo = NewsRepository()
    summarizer = NewsSummarizer(llm=LLMService())

    batch_service = SummaryBatchService(
        news_repo=news_repo,
        summarizer=summarizer,
        batch_size=5,
        pause_sec=15
    )

    batch_service.run()

if __name__ == "__main__":
    main()