from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from src.services.database.user_repository import UserRepository
from src.bot.keyboards.main import main_menu

TIME_LABELS = {
    "morning": "Утро ☀",
    "afternoon": "День 🌤",
    "evening": "Вечер 🌙"
}


def send_time_keyboard(selected: list[str]) -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text=f"{'🟢' if key in selected else '⚪'} {label}")]
        for key, label in TIME_LABELS.items()
    ]
    keyboard.append([KeyboardButton(text="⬅ Назад")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


class SendTimeHandlers:
    """Меню и настройка времени рассылки."""

    def __init__(self, user_repo: UserRepository):
        self.router = Router()
        self.user_repo = user_repo
        self.bot_messages: dict[int, int] = {}  # message_id последнего бота
        self.register()

    def register(self):
        self.router.message.register(self.menu, F.text == "⏰ Время рассылки")
        self.router.message.register(self.toggle_time, F.text.startswith(("🟢", "⚪")))
        self.router.message.register(self.back, F.text == "⬅ Назад")

    async def menu(self, message: Message):
        send_times = self.user_repo.get_settings(message.from_user.id).get("send_times", ["morning"])
        await self._send_screen(message, send_times)

    async def toggle_time(self, message: Message):
        send_times = self.user_repo.get_settings(message.from_user.id).get("send_times", [])

        for key, label in TIME_LABELS.items():
            if label in message.text:
                if key in send_times:
                    send_times.remove(key)
                else:
                    send_times.append(key)

        if not send_times:
            send_times = ["morning"]

        self.user_repo.set_setting(message.from_user.id, "send_times", send_times)
        await message.delete()

        old_msg_id = self.bot_messages.get(message.from_user.id)
        if old_msg_id:
            try:
                await message.bot.delete_message(message.chat.id, old_msg_id)
            except:
                pass

        bot_msg = await self._send_screen(message, send_times)
        self.bot_messages[message.from_user.id] = bot_msg.message_id

    async def _send_screen(self, message: Message, send_times: list[str]) -> Message:
        settings = self.user_repo.get_settings(message.from_user.id)
        subscribed = settings.get("subscribed", True)
        lang = settings.get("lang", "en")
        lang_name = "English" if lang == "en" else "Русский"
        send_times_text = ", ".join([TIME_LABELS[t] for t in send_times])

        text = (
            f"⚙ <b>Настройки</b>\n\n"
            f"⏰ Время рассылки: <b>{send_times_text}</b>\n"
            f"📩 Рассылка: <b>{'Включена' if subscribed else 'Отключена'}</b>\n"
            f"🌍 Язык: <b>{lang_name}</b>"
        )

        return await message.answer(text, parse_mode="HTML", reply_markup=send_time_keyboard(send_times))

    async def back(self, message: Message):
        await message.delete()
        old_msg_id = self.bot_messages.get(message.from_user.id)
        if old_msg_id:
            try:
                await message.bot.delete_message(message.chat.id, old_msg_id)
            except:
                pass
        await message.answer("🏠 Главное меню", reply_markup=main_menu())