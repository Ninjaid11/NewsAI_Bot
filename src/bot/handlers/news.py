from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from src.services.database.user_repository import UserRepository
from src.services.database.news_repository import NewsRepository
from src.services.database.sent_news_repository import SentNewsRepository
from src.services.news.news_processor import NewsProcessor
from src.services.news.news_summarizer import NewsSummarizer
from src.services.llm.llm_service import LLMService
from src.core.runtime import GENERATING_NEWS
from src.core.log_config import Logger

logger = Logger().get_logger()


class NewsHandler:
    """
    Кнопка "Новости" — выдаёт одну новость, которую пользователь ещё не видел.
    """

    def __init__(self, user_repo: UserRepository, news_repo: NewsRepository, sent_repo: SentNewsRepository):
        self.router = Router()
        self.user_repo = user_repo
        self.news_repo = news_repo
        self.sent_repo = sent_repo

        # создаём LLM и NewsProcessor
        llm = LLMService()
        summarizer = NewsSummarizer(llm)
        self.processor = NewsProcessor(summarizer, news_repo)

        self.register()

    def register(self):
        self.router.message.register(self.news, F.text == "📰 Новости")

    async def news(self, message: Message):
        user_id = message.from_user.id

        if user_id in GENERATING_NEWS:
            await message.answer("⏳ Подожди, я ещё генерирую новость…")
            return

        GENERATING_NEWS.add(user_id)
        try:
            try:
                lang = self.user_repo.get_setting(user_id, "lang", "en")
            except Exception as e:
                logger.error(f"Не удалось получить настройки пользователя {user_id}: {e}")
                lang = "en"

            try:
                news_list = self.news_repo.get_latest(20)
            except Exception as e:
                logger.error(f"Не удалось получить последние новости: {e}")
                news_list = []

            for item in news_list:
                try:
                    if self.sent_repo.was_sent(user_id, item["id"]):
                        continue

                    processed_news = self.processor.process(item, lang=lang)

                    title = processed_news["title"]
                    summary = processed_news["summary"]
                    published_at = processed_news["published_at"]
                    image_url = processed_news["image_url"]
                    source_url = processed_news["source_url"]

                    text = (
                        f"📰 <b>{title}</b>\n"
                        f"🕒 {published_at}\n\n"
                        f"<i>{summary}</i>"
                    )

                    keyboard = None
                    if source_url and source_url.startswith("http"):
                        keyboard = InlineKeyboardMarkup(
                            inline_keyboard=[[InlineKeyboardButton(text="Перейти к статье", url=source_url)]]
                        )

                    await message.answer_photo(
                        photo=image_url,
                        caption=text,
                        parse_mode="HTML",
                        reply_markup=keyboard
                    )

                    self.sent_repo.mark_sent(user_id, item["id"])
                    return
                except Exception as e:
                    logger.error(f"Ошибка при обработке новости для пользователя {user_id}: {e}")

            await message.answer("✅ Новых новостей пока нет")

        finally:
            GENERATING_NEWS.discard(user_id)