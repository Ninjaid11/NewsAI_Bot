from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

class SettingsHandlers:
    def __init__(self):
        self.router = Router()
        self.register_handlers()

    def register_handlers(self):
        self.router.message.register(self.menu, F.text == "Settings")

    async def menu(self, message: Message):
        await message.answer("⚙ Настройки пока недоступны, но скоро будут!")