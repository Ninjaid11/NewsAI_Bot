from src.services.llm.prompts import summary_prompt
from src.services.llm.llm_service import LLMService
from src.core.log_config import Logger

logger = Logger().get_logger()


class NewsSummarizer:
    """
    Обрабатывает новость через LLM
    """
    def __init__(self, llm: LLMService):
        self.llm = llm

    def summarize(self, *, title, content, published_at, lang: str) -> str:
        """
        Создает summary для одной новости на нужном языке

        return: Возвращает строку с кратким пересказом новости.
        """
        try:
            system, user_template = summary_prompt(lang)

            user_prompt = user_template.format(
                title=title,
                content=content,
                published_at=published_at
            )

            summary = self.llm.generate(
                system_instruction=system,
                user_prompt=user_prompt
            )

            return summary

        except Exception as e:
            logger.error(f"Ошибка генерации summary для новости '{title[:30]}...' lang={lang}: {e}")
            return ""