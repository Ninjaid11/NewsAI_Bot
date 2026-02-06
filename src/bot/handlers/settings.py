from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from src.services.database.user_repository import UserRepository
from src.bot.keyboards.main import main_menu

SEND_TIME_LABELS = {
    "morning": "Утро ☀",
    "afternoon": "День 🌤",
    "evening": "Вечер 🌙",
}

class SettingsHandlers:
    """Главное меню настроек ⚙."""

    def __init__(self, user_repo: UserRepository):
        self.router = Router()
        self.user_repo = user_repo
        self.bot_messages: dict[int, int] = {}
        self.register()

    def register(self):
        self.router.message.register(self.menu, F.text == "⚙ Настройки")
        self.router.message.register(self.back, F.text == "⬅ Назад")

    async def menu(self, message: Message):
        self.user_repo.ensure_user(message.from_user.id, message.from_user.full_name)

        settings = self.user_repo.get_settings(message.from_user.id)
        subscribed = settings.get("subscribed", True)
        lang = settings.get("lang", "en")
        send_times = settings.get("send_times", ["morning"])

        send_times_text = ", ".join(SEND_TIME_LABELS.get(t, t) for t in send_times)
        lang_name = "English" if lang == "en" else "Русский"

        text = (
            f"⚙ <b>Настройки</b>\n\n"
            f"⏰ Время рассылки: <b>{send_times_text}</b>\n"
            f"📩 Рассылка: <b>{'Включена' if subscribed else 'Отключена'}</b>\n"
            f"🌍 Язык: <b>{lang_name}</b>"
        )

        reply = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="⏰ Время рассылки")],
                [KeyboardButton(text="📩 Рассылка"), KeyboardButton(text="🌍 Язык")],
                [KeyboardButton(text="⬅ Назад")]
            ],
            resize_keyboard=True
        )

        # удаляем старое сообщение, если есть
        old_msg_id = self.bot_messages.get(message.from_user.id)
        if old_msg_id:
            try:
                await message.bot.delete_message(message.chat.id, old_msg_id)
            except:
                pass

        bot_msg = await message.answer(text, parse_mode="HTML", reply_markup=reply)
        self.bot_messages[message.from_user.id] = bot_msg.message_id

    async def back(self, message: Message):
        await message.delete()
        old_msg_id = self.bot_messages.get(message.from_user.id)
        if old_msg_id:
            try:
                await message.bot.delete_message(message.chat.id, old_msg_id)
            except:
                pass
        await message.answer("🏠 Главное меню", reply_markup=main_menu())