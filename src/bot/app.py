import asyncio
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.core.config import get_settings
from src.services.database.models import Database
from src.services.database.news_repository import NewsRepository


from src.bot.handlers.start import StartHandlers
from src.bot.handlers.settings import SettingsHandlers
from src.bot.handlers.news import NewsHandler

from src.services.llm.service import LLMService
from src.services.news.service import NewsService
from src.services.parser.rss_parser import RSSParser


class BotApplication:
    def  __init__(self):
        self.settings = get_settings()

        self.bot = Bot(token=self.settings.BOT_TOKEN)
        self.dp = Dispatcher()

        # Сервисы
        self.news_service = NewsService()
        self.llm_service = LLMService()
        self.news_repo = NewsRepository()
        self.database = Database()

        # parser
        self.rss_parser = RSSParser(
            rss_list=self.settings.RSS_SOURCES,
            llm=self.llm_service,
            db=self.news_repo,
        )

        self.scheduler = AsyncIOScheduler()

    def setup_handlers(self):
        start = StartHandlers()
        settings = SettingsHandlers()
        news = NewsHandler(self.news_service, self.llm_service)

        self.dp.include_router(start.router)
        self.dp.include_router(settings.router)
        self.dp.include_router(news.router)

    def setup_tasks(self):
        self.scheduler.add_job(self.rss_parser.fetch_all, "interval", hours=1)
        self.scheduler.start()

    async def run(self):
        self.database.create_tables()
        self.setup_handlers()
        self.setup_tasks()

        await self.rss_parser.fetch_all()
        print("Parser + scheduler started")
        print("Bot started...")

        await self.bot.delete_webhook(drop_pending_updates=True)
        await self.dp.start_polling(self.bot)