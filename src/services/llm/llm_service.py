import time
from google import genai
from google.genai import types
from google.genai.errors import ClientError

from src.core.config import get_settings
from src.core.log_config import Logger

logger = Logger().get_logger()


class LLMService:
    def __init__(self):
        settings = get_settings()
        self.model = genai.Client(api_key=settings.API_KEY)
        self.model_name = "gemini-2.5-flash"

    def generate(
        self,
        system_instruction: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_output_tokens: int = 400
    ) -> str:
        try:
            response = self.model.models.generate_content(
                model=self.model_name,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens
                ),
                contents=[
                    types.Content(
                        role="user",
                        parts=[types.Part(text=user_prompt)]
                    )
                ],
            )

            text = response.text.strip()
            return text

        except ClientError as e:
            error_str = str(e)
            logger.error(f"Ошибка LLMClient: {error_str}")

            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                logger.warning("Лимит запросов LLM превышен, пауза 15 секунд...")
                time.sleep(15)
                return self.generate(
                    system_instruction=system_instruction,
                    user_prompt=user_prompt,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens
                )
            raise
        except Exception as e:
            logger.error(f"Неожиданная ошибка в LLMService: {e}")
            raise