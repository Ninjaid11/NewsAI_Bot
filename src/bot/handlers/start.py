from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

class StartHandlers:
    def __init__(self):
        self.router = Router()
        self.register_handlers()

    def register_handlers(self):
        self.router.message.register(self.start, CommandStart())

    async def start(self, message: Message):
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="News")],
                [KeyboardButton(text="Settings")],
            ],
            resize_keyboard=True
        )

        await message.answer(
            "👋 Привет! Я твой умный помощник.\n\n"
            "🔹 Новости\n"
            "🔹 Настройки аккаунта\n\n"
            "Что хочешь сделать?",
            reply_markup=keyboard
        )