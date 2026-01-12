from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

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

        # Берём последние 20 новостей
        news_list = self.news_repo.get_latest(20)

        # Ищем первую непрочитанную
        for item in news_list:
            if not self.sent_repo.was_sent(user_id, item["id"]):
                text = (
                    f"📰 <b>{item['title']}</b>\n"
                    
                    f"🔗 {item['source_url']}"
                )
                await message.answer(text, parse_mode="HTML")

                # Помечаем как отправленную
                self.sent_repo.mark_sent(user_id, item["id"])
                break
        else:
            await message.answer("✅ Новостей больше нет. Подождите, пока появятся новые!")
