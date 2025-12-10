import asyncio

from aiogram import Bot, Dispatcher

from src.core.config import get_settings
from src.services.database.models import Database

from src.bot.handlers.start import StartHandlers
from src.bot.handlers.settings import SettingsHandlers
from src.bot.handlers.news import NewsHandler

from src.services.llm.service import LLMService
from src.services.news.service import NewsService


class BotApplication:
    def  __init__(self):
        self.settings = get_settings()
        self.db = Database()
        self.bot = Bot(token=self.settings.BOT_TOKEN)
        self.dp = Dispatcher()

        # Сервисы
        self.news_service = NewsService()
        self.llm_service = LLMService()

        # Хендлеры
        self.start_handlers = StartHandlers()
        self.settings_handlers = SettingsHandlers()
        self.news_handlers = NewsHandler(self.news_service, self.llm_service)

    def setup(self):
        self.db.create_tables()

        self.dp.include_router(self.start_handlers.router)
        self.dp.include_router(self.settings_handlers.router)
        self.dp.include_router(self.news_handlers.router)

    async def run(self):
        self.setup()
        print("Bot started...")

        await self.bot.delete_webhook(drop_pending_updates=True)
        await self.dp.start_polling(self.bot)

if __name__ == "__main__":
    app = BotApplication()
    asyncio.run(app.run())