from googletrans import Translator
from src.core.log_config import Logger

logger = Logger().get_logger()

_translator = Translator()

async def translate_to_ru(text: str) -> str:
    if not text:
        return ""
    try:
        result = await _translator.translate(text, src='en', dest='ru')
        return result.text
    except Exception as e:
        logger.error(f"Ошибка перевода текста на русский: '{text[:30]}...': {e}")
        return text