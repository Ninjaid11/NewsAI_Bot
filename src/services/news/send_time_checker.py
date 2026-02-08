from datetime import datetime

class SendTimeChecker:
    """Проверяет, нужно ли слать новость сейчас."""

    TIME_MAP = {
        "morning": 8,
        "afternoon": 13,
        "evening": 18
    }

    @staticmethod
    def should_send_now(send_times: list[str], use_utc=True) -> bool:
        """
        send_times — ['morning', 'evening']
        """
        now = datetime.utcnow() if use_utc else datetime.now()

        # ⛔ отправляем ТОЛЬКО в начале часа
        if now.minute != 0:
            return False

        for period in send_times:
            if SendTimeChecker.TIME_MAP.get(period) == now.hour:
                return True
        return False