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
from src.bot.handlers.send_time import SendTimeHandlers
from src.bot.handlers.language import LanguageHandlers
from src.bot.handlers.subscription import SubscriptionHandlers

from src.services.llm.llm_service import LLMService
from src.services.news.mailer import NewsMailer
from src.services.parser.rss_parser import RSSParser

from src.core.log_config import Logger

logger = Logger().get_logger()

class BotApplication:
    def __init__(self):
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
        self.news_mailer = NewsMailer(
            bot=self.bot,
            users=self.user_repo,
            news=self.news_repo,
            sent=self.sent_repo
        )

        # parser
        self.rss_parser = RSSParser(
            rss_list=self.settings.RSS_SOURCES,
            news_repo=self.news_repo,
        )

        self.scheduler = AsyncIOScheduler()

    def setup_handlers(self):
        try:
            start = StartHandlers(self.user_repo)
            settings = SettingsHandlers(self.user_repo)
            news = NewsHandler(self.user_repo, self.news_repo, self.sent_repo)
            send_time = SendTimeHandlers(self.user_repo)
            lang = LanguageHandlers(self.user_repo)
            subscribe = SubscriptionHandlers(self.user_repo)

            self.dp.include_router(start.router)
            self.dp.include_router(settings.router)
            self.dp.include_router(news.router)
            self.dp.include_router(send_time.router)
            self.dp.include_router(lang.router)
            self.dp.include_router(subscribe.router)
        except Exception as e:
            logger.error(f"Ошибка при настройке хэндлеров: {e}")

    def setup_tasks(self):
        try:
            self.scheduler.add_job(self.news_mailer.send_new_news, "interval", hours=1)
            self.scheduler.start()
        except Exception as e:
            logger.error(f"Ошибка при настройке scheduler: {e}")

    async def run(self):
        try:
            self.database.create_tables()

            self.setup_handlers()
            self.setup_tasks()

            await self.rss_parser.fetch_all()

            await self.news_mailer.send_new_news()
            logger.info("Бот стартовал...")
            await self.bot.delete_webhook(drop_pending_updates=True)

            await self.dp.start_polling(self.bot)
        except Exception as e:
            logger.error(f"Критическая ошибка при запуске бота: {e}")