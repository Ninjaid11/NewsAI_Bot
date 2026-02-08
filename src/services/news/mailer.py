from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.services.database.user_repository import UserRepository
from src.services.database.news_repository import NewsRepository
from src.services.database.sent_news_repository import SentNewsRepository

from src.services.news.news_processor import NewsProcessor
from src.services.news.news_summarizer import NewsSummarizer
from src.services.news.send_time_checker import SendTimeChecker

from src.services.llm.llm_service import LLMService
from src.core.log_config import Logger

logger = Logger().get_logger()

class NewsMailer:
    """Сервис рассылки новостей с учётом времени."""

    FALLBACK_IMAGE = "static/images/fallback.jpg"

    def __init__(self, bot, users: UserRepository, news: NewsRepository, sent: SentNewsRepository):
        self.bot = bot
        self.users = users
        self.news = news
        self.sent = sent

        llm = LLMService()
        summarizer = NewsSummarizer(llm)
        self.processor = NewsProcessor(summarizer, news)

    async def send_new_news(self):
        try:
            user_ids = self.users.get_subscribed_users()
        except Exception as e:
            logger.error(f"Ошибка получения пользователей: {e}")
            return

        for user_id in user_ids:
            try:
                settings = self.users.get_settings(user_id)
                send_times = settings.get("send_times", ["morning"])
                lang = settings.get("lang", "en")

                if not SendTimeChecker.should_send_now(send_times, use_utc=False):
                    continue

                news_list = self.news.get_latest(20)

            except Exception as e:
                logger.error(f"Ошибка настроек user_id={user_id}: {e}")
                continue

            for item in news_list:
                try:
                    if self.sent.was_sent(user_id, item["id"]):
                        continue

                    processed = self.processor.process(item, lang=lang)

                    text = (
                        f"📰 <b>{processed['title']}</b>\n"
                        f"🕒 {processed['published_at']}\n\n"
                        f"<i>{processed['summary']}</i>"
                    )

                    keyboard = None
                    if processed.get("source_url"):
                        keyboard = InlineKeyboardMarkup(
                            inline_keyboard=[
                                [InlineKeyboardButton(text="Перейти к статье", url=processed["source_url"])]
                            ]
                        )

                    await self.bot.send_photo(
                        chat_id=user_id,
                        photo=processed.get("image_url") or self.FALLBACK_IMAGE,
                        caption=text,
                        parse_mode="HTML",
                        reply_markup=keyboard
                    )

                    self.sent.mark_sent(user_id, item["id"])
                    logger.info(f"Новость отправлена user_id={user_id}, news_id={item['id']}")
                    break

                except Exception as e:
                    logger.error(f"Ошибка отправки news_id={item['id']} user_id={user_id}: {e}")