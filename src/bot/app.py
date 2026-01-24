import asyncio
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.core.config import get_settings
from src.services.database.models import Database
from src.services.database.news_repository import NewsRepository
from src.services.database.user_repository import UserRepository
from src.services.database.sent_news_repository import SentNewsRepository


from src.bot.handlers.start import StartHandlers
from src.bot.handlers.settings import SettingsHandlers
from src.bot.handlers.news import NewsHandler

from src.services.llm.llm_service import LLMService
from src.services.news.mailer import NewsMailer
from src.services.parser.rss_parser import RSSParser


class BotApplication:
    def  __init__(self):
        self.settings = get_settings()

        self.bot = Bot(token=self.settings.BOT_TOKEN)
        self.dp = Dispatcher()

        # database
        self.database = Database()
        self.news_repo = NewsRepository()
        self.user_repo = UserRepository()
        self.sent_repo = SentNewsRepository()

        # Сервисы
        self.llm_service = LLMService()
        self.news_repo = NewsRepository()
        self.news_mailer = NewsMailer(
            bot=self.bot,
            users=self.user_repo,
            news=self.news_repo,
            sent=self.sent_repo
        )

        # parser
        self.rss_parser = RSSParser(
            rss_list=self.settings.RSS_SOURCES,
            llm=self.llm_service,
            news_repo=self.news_repo,
        )

        self.scheduler = AsyncIOScheduler()

    def setup_handlers(self):
        start = StartHandlers(self.user_repo)
        settings = SettingsHandlers(self.user_repo)
        news = NewsHandler(self.user_repo, self.news_repo, self.sent_repo)

        self.dp.include_router(start.router)
        self.dp.include_router(settings.router)
        self.dp.include_router(news.router)

    def setup_tasks(self):
        self.scheduler.add_job(self.news_mailer.send_new_news, "interval", hours=1)
        self.scheduler.start()

    async def run(self):
        self.database.create_tables()
        self.setup_handlers()
        self.setup_tasks()

        await self.rss_parser.fetch_all()
        await self.news_mailer.send_new_news()

        print("Bot started...")

        await self.bot.delete_webhook(drop_pending_updates=True)
        await self.dp.start_polling(self.bot)