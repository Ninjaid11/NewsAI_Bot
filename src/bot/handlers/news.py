from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from src.services.database.user_repository import UserRepository
from src.services.database.news_repository import NewsRepository
from src.services.database.sent_news_repository import SentNewsRepository

class NewsHandler:
    """
    Кнопка "Новости" — выдаёт одну новость, которую пользователь ещё не видел.
    """
    def __init__(self, user_repo: UserRepository, news_repo: NewsRepository, sent_repo: SentNewsRepository):
        self.router = Router()
        self.user_repo = user_repo
        self.news_repo = news_repo
        self.sent_repo = sent_repo
        self.register()

    def register(self):
        self.router.message.register(self.news, F.text == "📰 Новости")

    async def news(self, message: Message):
        user_id = message.from_user.id
        news_list = self.news_repo.get_latest(20)

        for item in news_list:
            if self.sent_repo.was_sent(user_id, item["id"]):
                continue

            published_at = item.get("published_at", "")
            if published_at:
                dt = datetime.fromisoformat(published_at)
                published_at = dt.strftime("%d %B %Y, %H:%M")

            text = f"📰 <b>{item.get("title")}</b>\n🕒 {published_at}\n\n" \
                   f"<i>{item.get("summary")}</i>"

            url = item.get("source_url")
            keyboard = None
            if url and url.startswith("http"):
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[[InlineKeyboardButton(text="Перейти к статье", url=url)]]
                )

            image_url = item.get("image_url")
            if not image_url:
                image_url = "https://via.placeholder.com/500x300.png?text=News"

            await message.answer_photo(
                photo=image_url,
                caption=text,
                parse_mode="HTML",
                reply_markup=keyboard
            )

            self.sent_repo.mark_sent(user_id, item["id"])

            return

        await message.answer("✅ Новых новостей пока нет")