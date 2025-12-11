class LLMService:
    async def summarize(self, text: str) -> str:
        if len(text) > 200:
            return text[:200] + "..."
        return text