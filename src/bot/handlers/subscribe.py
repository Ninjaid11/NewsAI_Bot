from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from src.services.database.user_repository import UserRepository


class SubscribeHandler:
    """
    Обработчик команд подписки и отписки от новостей.
    Управляет статусом подписки пользователя в базе данных.
    """
    def __init__(self, repo: UserRepository):
        self.router = Router()
        self.register()
        self.repo = repo

    def register(self):
        self.router.message.register(self.subscribe, Command("subscribe"))
        self.router.message.register(self.unsubscribe, Command("unsubscribe"))

    async def subscribe(self, message: Message):
        user = message.from_user

        self.repo.add_or_update(
            telegram_id=user.id,
            name=user.full_name
        )

        await message.answer("✅ Ты подписался на новости!")


    async def unsubscribe(self, message: Message):
        self.repo.unsubscribe(message.from_user.id)
        await message.answer("❌ Ты отписался от новостей")
