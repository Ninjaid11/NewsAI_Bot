import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

class Logger:
    """Класс для настройки логирования всего проекта"""

    LOG_DIR = Path("logs")
    LOG_FILE = LOG_DIR / "app.log"

    def __init__(self, level: int = logging.INFO):
        self.LOG_DIR.mkdir(exist_ok=True)
        self.logger = logging.getLogger("AppLogger")
        self.logger.setLevel(level)
        self._setup_handlers(level)

    def _setup_handlers(self, level: int) -> None:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        )

        # Файловый обработчик с ротацией
        file_handler = RotatingFileHandler(
            filename=self.LOG_FILE,
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)

        # Консольный обработчик
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)

        # Удаляем старые обработчики, если есть
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def get_logger(self) -> logging.Logger:
        return self.logger