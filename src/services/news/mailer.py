from datetime import datetime


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.services.database.user_repository import UserRepository
from src.services.database.news_repository import NewsRepository
from src.services.database.sent_news_repository import SentNewsRepository

class NewsMailer:
    """
    Сервис рассылки новостей пользователям.
    Отправляет одну новую новость подписанным пользователям
    и фиксирует факт отправки в базе данных.
    """

    FALLBACK_IMAGE = "https://via.placeholder.com/500x300.png?text=News"

    def __init__(self, bot, users: UserRepository, news: NewsRepository, sent: SentNewsRepository):
        self.bot = bot
        self.users = users
        self.news = news
        self.sent = sent

    async def send_new_news(self):
        """
        Отправляет одну новость каждому подписанному пользователю.
        Проверяет, была ли новость уже отправлена.
        """
        subscribed_users = self.users.get_subscribed_users()

        for user_id in subscribed_users:
            lang = self.users.get_setting(user_id, "lang", "en")

            news_list = self.news.get_latest(20)

            for item in news_list:
                if self.sent.was_sent(user_id, item["id"]):
                    continue

                published_at = item.get("published_at", "")
                if published_at:
                    try:
                        dt = datetime.fromisoformat(published_at)
                        published_at = dt.strftime("%d %B %Y, %H:%M")
                    except Exception:
                        pass

                title = item.get("title", "")
                summary = item.get("summary", "")

                if lang == "ru":
                    summary = f"[RU] {summary}"
                else:
                    summary = f"[EN] {summary}"

                text = (
                    f"📰 <b>{title}</b>\n"
                    f"🕒 {published_at}\n\n"
                    f"<i>{summary}</i>"
                )

                keyboard = None
                url = item.get("source_url")
                if url and url.startswith("http"):
                    keyboard = InlineKeyboardMarkup(
                        inline_keyboard=[[InlineKeyboardButton(text="Перейти к статье", url=url)]]
                    )

                image_url = item.get("image_url") or self.FALLBACK_IMAGE

                await self.bot.send_photo(
                    chat_id=user_id,
                    photo=image_url,
                    caption=text,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )

                self.sent.mark_sent(user_id, item["id"])

                break