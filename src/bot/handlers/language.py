from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from src.services.database.user_repository import UserRepository
from src.bot.keyboards.main import main_menu

# Словарь с доступными языками и их метками
LANG_LABELS = {
    "en": "🇬🇧 English",
    "ru": "🇷🇺 Русский"
}

# Функция для создания клавиатуры выбора языка
def language_keyboard(selected: str) -> ReplyKeyboardMarkup:
    """
    Создаёт ReplyKeyboardMarkup с языками.
    """
    keyboard = [
        [KeyboardButton(text=f"{label} ✅" if code == selected else label)]
        for code, label in LANG_LABELS.items()
    ]
    keyboard.append([KeyboardButton(text="⬅ Назад")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


class LanguageHandlers:
    """Меню выбора языка новостей."""

    def __init__(self, user_repo: UserRepository):
        self.router = Router()
        self.user_repo = user_repo
        # Словарь для хранения ID сообщений бота, чтобы их можно было удалять
        self.bot_messages: dict[int, int] = {}
        self.register()

    def register(self):
        self.router.message.register(self.menu, F.text == "🌍 Язык")
        self.router.message.register(self.set_language, F.text.startswith(tuple(LANG_LABELS.values())))
        self.router.message.register(self.back, F.text == "⬅ Назад")

    async def menu(self, message: Message):
        """
        Отображение меню выбора языка.
        Удаляет предыдущее сообщение бота, чтобы не дублировалось.
        """
        lang = self.user_repo.get_settings(message.from_user.id).get("lang", "en")

        old_msg_id = self.bot_messages.get(message.from_user.id)
        if old_msg_id:
            try:
                await message.bot.delete_message(message.chat.id, old_msg_id)
            except:
                pass

        bot_msg = await self._send_screen(message, lang)
        self.bot_messages[message.from_user.id] = bot_msg.message_id

    async def set_language(self, message: Message):
        """
        Обработка нажатия на кнопку выбора языка.
        Сохраняет выбор в БД, удаляет старое сообщение бота и пользователя,
        обновляет меню с выделением выбранного языка.
        """
        btn_label = message.text.replace(" ✅", "")
        selected = next((code for code, label in LANG_LABELS.items() if label == btn_label), None)
        if not selected:
            return

        self.user_repo.set_setting(message.from_user.id, "lang", selected)

        old_msg_id = self.bot_messages.get(message.from_user.id)
        if old_msg_id:
            try:
                await message.bot.delete_message(message.chat.id, old_msg_id)
            except:
                pass

        bot_msg = await self._send_screen(message, selected)
        self.bot_messages[message.from_user.id] = bot_msg.message_id

        await message.delete()

    async def _send_screen(self, message: Message, selected: str):
        """
        Вспомогательная функция для отправки меню выбора языка.
        Отправляет текст и клавиатуру с текущим выбранным языком.
        """
        text = f"🌍 <b>Выбери язык новостей</b>\nСейчас: {LANG_LABELS[selected]}"
        return await message.answer(text, parse_mode="HTML", reply_markup=language_keyboard(selected))

    async def back(self, message: Message):
        """
        Обработка кнопки "Назад".
        Удаляет старое сообщение бота и пользователя, затем открывает главное меню.
        """
        old_msg_id = self.bot_messages.get(message.from_user.id)
        if old_msg_id:
            try:
                await message.bot.delete_message(message.chat.id, old_msg_id)
            except:
                pass

        await message.delete()

        await message.answer("🏠 Главное меню", reply_markup=main_menu())