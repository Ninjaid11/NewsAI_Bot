from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

from src.services.database.user_repository import UserRepository

class StartHandlers:
    """
    Обработчик команды /start.
    Отвечает за приветствие пользователя и первичное взаимодействие с ботом.
    """
    def __init__(self, user_repo: UserRepository):
        self.router = Router()
        self.user_repo = user_repo
        self.register()

    def register(self):
        self.router.message.register(self.start, CommandStart())

    async def start(self, message: Message):
        self.user_repo.add_or_update(
            telegram_id=message.from_user.id,
            name=message.from_user.full_name
        )

        await message.answer(
            "👋 Привет!\nЯ бот с умными новостями 🧠📰\n\n"
            "Выбери действие:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="📰 Новости")],
                    [KeyboardButton(text="⚙ Настройки")]
                ],
                resize_keyboard=True
            )
        )