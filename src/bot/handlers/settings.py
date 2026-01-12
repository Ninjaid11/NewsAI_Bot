from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from src.services.database.user_repository import UserRepository
from src.bot.keyboards.main import main_menu

class SettingsHandlers:
    """
    Настройки пользователя Telegram-бота.
    Позволяет менять интервал рассылки и включать/отключать рассылку.
    """
    def __init__(self, user_repo: UserRepository):
        self.router = Router()
        self.user_repo = user_repo
        self.register()

    def register(self):
        self.router.message.register(self.menu, F.text == "⚙ Настройки")
        self.router.message.register(self.set_interval, F.text.in_(["1 час", "3 часа", "6 часов"]))
        self.router.message.register(self.toggle_subscription, F.text.in_(["Включить рассылку", "Отключить рассылку"]))
        self.router.message.register(self.back, F.text == "⬅ Назад")

    async def menu(self, message: Message):
        settings = self.user_repo.get_settings(message.from_user.id)
        subscribed = settings.get("subscribed", True)
        interval = settings.get("news_interval", 1)

        text = (
            f"⚙ <b>Настройки</b>\n\n"
            f"⏱ Интервал рассылки: <b>{interval} час(ов)</b>\n"
            f"📩 Рассылка: <b>{'Включена' if subscribed else 'Отключена'}</b>"
        )

        reply = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="1 час"), KeyboardButton(text="3 часа"), KeyboardButton(text="6 часов")],
                [KeyboardButton(text="Включить рассылку"), KeyboardButton(text="Отключить рассылку")],
                [KeyboardButton(text="⬅ Назад")]
            ],
            resize_keyboard=True
        )

        await message.answer(text, parse_mode="HTML", reply_markup=reply)

    async def set_interval(self, message: Message):
        interval_map = {"1 час": 1, "3 часа": 3, "6 часов": 6}
        interval = interval_map.get(message.text, 1)

        settings = self.user_repo.get_settings(message.from_user.id)
        settings["news_interval"] = interval
        self.user_repo.update_settings(message.from_user.id, settings)

        await message.answer(f"✅ Интервал рассылки установлен на {interval} час(ов)")

    async def toggle_subscription(self, message: Message):
        settings = self.user_repo.get_settings(message.from_user.id)
        settings["subscribed"] = True if "Включить" in message.text else False
        self.user_repo.update_settings(message.from_user.id, settings)

        await message.answer(f"✅ Рассылка {'включена' if settings['subscribed'] else 'отключена'}")

    async def back(self, message: Message):
        await message.answer(
            "🏠 Главное меню",
            reply_markup=main_menu()
        )