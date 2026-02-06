from datetime import datetime

class SendTimeChecker:
    """Проверяет, нужно ли слать новость сейчас, по выбранным периодам рассылки."""

    # Карта периодов и соответствующих часов
    TIME_MAP = {
        "morning": 8,  # утро в 8:00
        "afternoon": 13,  # день в 13:00
        "evening": 18  # вечер в 18:00
    }

    @staticmethod
    def should_send_now(send_times: list[str], use_utc=True) -> bool:
        """
        Проверяет, совпадает ли текущий час с выбранными пользователем периодами.
        send_times: список ключей из TIME_MAP
        use_utc: True — использовать UTC, False — локальное время
        """
        now_hour = datetime.utcnow().hour if use_utc else datetime.now().hour

        for period in send_times:
            if SendTimeChecker.TIME_MAP.get(period) == now_hour:
                return True
        return False