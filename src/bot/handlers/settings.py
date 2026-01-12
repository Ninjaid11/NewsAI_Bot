from idlelib.window import add_windows_to_menu

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart, Command
from aiohttp.web_routedef import delete

from src.services.database.user_repository import UserRepository
from src.bot.keyboards.main import main_menu

class SettingsHandlers:
    """
    Обработчик команд и действий пользователя,
    связанных с настройками Telegram-бота.
    """
    def __init__(self, user_repo: UserRepository):
        self.router = Router()
        self.user_repo = user_repo
        self.register()

    def register(self):
        self.router.message.register(self.menu, F.text == "⚙ Настройки")
        self.router.message.register(self.set_limit, F.text.in_(["3 новости", "5 новостей"]))
        self.router.message.register(self.back, F.text.in_(["⬅ Назад"]))

    async def menu(self, message: Message):
        settings = self.user_repo.get_settings(message.from_user.id)

        await message.answer(
            f"⚙ <b>Настройки</b>\n\n"
            f"📰 Новостей за раз: <b>{settings.get('news_limit', 5)}</b>",
            parse_mode="HTML",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="3 новости"), KeyboardButton(text="5 новостей")],
                    [KeyboardButton(text="⬅ Назад")]
                ],
                resize_keyboard=True
            )
        )

    async def set_limit(self, message: Message):
            limit = 3 if "3" in message.text else 5

            settings = self.user_repo.get_settings(message.from_user.id)
            settings["news_limit"] = limit
            self.user_repo.update_settings(message.from_user.id, settings)

            await message.answer(
            f"✅ Теперь будет {limit} новостей за раз",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [KeyboardButton(text="⬅ Назад")]
                    ],
                    resize_keyboard=True
                )
            )

    async def back(self, message: Message):
        await message.delete()

        await message.answer(
            "🏠 Главное меню",
            reply_markup=main_menu()
        )