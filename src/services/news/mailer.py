from src.services.database.user_repository import UserRepository
from src.services.database.news_repository import NewsRepository
from src.services.database.sent_news_repository import SentNewsRepository

class NewsMailer:
    """
    Сервис рассылки новостей пользователям.
    Отправляет одну новую новость подписанным пользователям
    и фиксирует факт отправки в базе данных.
    """
    def __init__(self, bot, users: UserRepository, news: NewsRepository, sent: SentNewsRepository):
        self.bot = bot
        self.users = users
        self.news = news
        self.sent = sent

    async def send_new_news(self):
        users = self.users.get_subscribed_users()
        news_list = self.news.get_latest(20)

        for user_id in users:
            for item in news_list:
                if self.sent.was_sent(user_id, item["id"]):
                    continue

                text = (
                    f"📰 <b>{item['title']}</b>\n"
                    #f"{item.get('summary', '')}\n"
                    f"🔗 {item['source_url']}"
                )

                await self.bot.send_message(user_id, text, parse_mode="HTML")
                self.sent.mark_sent(user_id, item["id"])
                break