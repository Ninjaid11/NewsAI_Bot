from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from src.services.database.user_repository import UserRepository
from src.bot.keyboards.main import main_menu

SUB_LABELS = {
    True: "Включить рассылку",
    False: "Отключить рассылку"
}

def subscription_keyboard(selected: bool) -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text=f"{label} ✅" if selected == key else label)]
        for key, label in SUB_LABELS.items()
    ]
    keyboard.append([KeyboardButton(text="⬅ Назад")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

class SubscriptionHandlers:
    """Меню подписки на новости."""

    def __init__(self, user_repo: UserRepository):
        self.router = Router()
        self.user_repo = user_repo
        self.bot_messages: dict[int, int] = {}
        self.register()

    def register(self):
        self.router.message.register(self.menu, F.text == "📩 Рассылка")
        self.router.message.register(self.toggle_subscription, F.text.startswith(tuple(SUB_LABELS.values())))
        self.router.message.register(self.back, F.text == "⬅ Назад")

    async def menu(self, message: Message):
        subscribed = self.user_repo.get_settings(message.from_user.id).get("subscribed", True)
        old_msg_id = self.bot_messages.get(message.from_user.id)
        if old_msg_id:
            try:
                await message.bot.delete_message(message.chat.id, old_msg_id)
            except:
                pass
        bot_msg = await self._send_screen(message, subscribed)
        self.bot_messages[message.from_user.id] = bot_msg.message_id

    async def toggle_subscription(self, message: Message):
        selected_label = message.text.replace(" ✅", "")
        selected = next((key for key, label in SUB_LABELS.items() if label == selected_label), None)
        if selected is None:
            return

        self.user_repo.set_setting(message.from_user.id, "subscribed", selected)

        old_msg_id = self.bot_messages.get(message.from_user.id)
        if old_msg_id:
            try:
                await message.bot.delete_message(message.chat.id, old_msg_id)
            except:
                pass

        bot_msg = await self._send_screen(message, selected)
        self.bot_messages[message.from_user.id] = bot_msg.message_id

        await message.delete()

    async def _send_screen(self, message: Message, selected: bool):
        text = f"📩 <b>Подписка на новости</b>\nСейчас: {SUB_LABELS[selected]}"
        return await message.answer(text, parse_mode="HTML", reply_markup=subscription_keyboard(selected))

    async def back(self, message: Message):
        old_msg_id = self.bot_messages.get(message.from_user.id)
        if old_msg_id:
            try:
                await message.bot.delete_message(message.chat.id, old_msg_id)
            except:
                pass
        await message.delete()
        await message.answer("🏠 Главное меню", reply_markup=main_menu())