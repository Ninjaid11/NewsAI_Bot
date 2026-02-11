from datetime import datetime
from zoneinfo import ZoneInfo

class SendTimeChecker:
    """Проверяет, нужно ли слать новость прямо сейчас по Киеву."""

    TIME_MAP = {
        "morning": 8,
        "afternoon": 13,
        "evening": 18
    }

    @staticmethod
    def should_send_now(send_times: list[str]) -> bool:
        """send_times — список ['morning', 'evening', ...]"""
        now = datetime.now(ZoneInfo("Europe/Kyiv"))

        # Отправляем только в начале часа (минуты 0 или 1)
        if now.minute > 1:
            return False

        for period in send_times:
            if SendTimeChecker.TIME_MAP.get(period) == now.hour:
                return True
        return False