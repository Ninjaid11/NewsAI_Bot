from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from src.services.database.news_repository import NewsRepository
from src.services.database.user_repository import UserRepository


class NewsHandler:
    """
    Обработчик команд, связанных с новостями.
    Позволяет пользователю получать последние новости из базы данных
    через Telegram-бота.
    """
    def __init__(self, repo: NewsRepository, user_repo: UserRepository):
        self.router = Router()
        self.register()
        self.repo = repo
        self.user_repo = user_repo

    def register(self):
        self.router.message.register(self.news, F.text == "📰 Новости")

    async def news(self, message: Message):
        settings = self.user_repo.get_settings(message.from_user.id)
        limit = settings.get("news_limit", 5)

        news_list = self.repo.get_latest(limit)

        if not news_list:
            await message.answer("📰 Пока новостей нет")
            return

        for item in news_list:
            text = (
                f"📰 <b>{item['title']}</b>\n"
                f"🔗 {item['source_url']}"
            )

            await message.answer(text, parse_mode="HTML")
