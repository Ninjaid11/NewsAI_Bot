import asyncio

from aiogram import Bot, Dispatcher

from src.core.config import get_settings
from src.services.database.crud import create_tables
from src.services.llm.service import LLMService
from src.services.news.service import NewsService

settings = get_settings()

async def main():
    create_tables()
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    # Инициализируем сервисы
    news_service = NewsService()
    llm_service = LLMService()

    # Подключаем handler через класс
    news_handler = NewsHandler(news_service, llm_service)
    dp.include_router(news_handler.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run()