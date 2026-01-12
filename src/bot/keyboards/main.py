from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📰 Новости")],
            [KeyboardButton(text="⚙ Настройки")]
        ],
        resize_keyboard=True
    )