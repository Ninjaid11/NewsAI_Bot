from datetime import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.services.database.user_repository import UserRepository
from src.services.database.news_repository import NewsRepository
from src.services.database.sent_news_repository import SentNewsRepository
from src.services.news.news_processor import NewsProcessor
from src.services.news.news_summarizer import NewsSummarizer
from src.services.llm.llm_service import LLMService

class NewsMailer:
    """
    Сервис рассылки новостей пользователям.
    Генерирует summary при необходимости ПЕРЕД отправкой.
    """
    def __init__(
        self,
        bot,
        users: UserRepository,
        news: NewsRepository,
        sent: SentNewsRepository
    ):
        self.bot = bot
        self.users = users
        self.news = news
        self.sent = sent
        llm = LLMService()
        summarizer = NewsSummarizer(llm)
        self.processor = NewsProcessor(summarizer, news)

    async def send_new_news(self):
        """
        Отправляет одну новую новость каждому подписанному пользователю.
        summary генерируется при необходимости.
        """
        subscribed_users = self.users.get_subscribed_users()

        for user_id in subscribed_users:
            lang = self.users.get_setting(user_id, "lang", "en")
            news_list = self.news.get_latest(20)

            for item in news_list:
                if self.sent.was_sent(user_id, item["id"]):
                    continue

                processed = self.processor.process(item, lang=lang)

                text = (
                    f"📰 <b>{processed['title']}</b>\n"
                    f"🕒 {processed['published_at']}\n\n"
                    f"<i>{processed['summary']}</i>"
                )

                keyboard = None
                url = processed.get("source_url")
                if url and url.startswith("http"):
                    keyboard = InlineKeyboardMarkup(
                        inline_keyboard=[
                            [InlineKeyboardButton(text="Перейти к статье", url=url)]
                        ]
                    )

                image_url = processed.get("image_url") or self.FALLBACK_IMAGE

                await self.bot.send_photo(
                    chat_id=user_id,
                    photo=image_url,
                    caption=text,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )

                self.sent.mark_sent(user_id, item["id"])
                break