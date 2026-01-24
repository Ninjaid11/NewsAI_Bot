from google import genai
from google.genai import types

from src.core.config import get_settings

class LLMService:
    def __init__(self):
        settings = get_settings()
        self.model = genai.Client(api_key=settings.API_KEY)
        self.model_name = "gemini-2.5-flash"

    def generate(self, system_instruction: str, user_prompt: str, temperature: float = 0.7, max_output_tokens: int = 400) -> str:

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

        return response.text.strip()