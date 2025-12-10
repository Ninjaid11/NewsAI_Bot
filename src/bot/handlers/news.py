from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command


class NewsHandler:
    def __init__(self, news_service, llm_service):
        self.router = Router()
        self.news_service = news_service
        self.llm_service = llm_service
        self.register_handlers()

    def register_handlers(self):
        self.router.message.register(self.menu, F.text =="News")

    async def menu(self, message: Message):
        await message.answer("📰 Новости пока в разработке!")
