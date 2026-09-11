from anthropic import AsyncAnthropic

from app.config import settings
from app.core.providers.base import LLMProvider


class AnthropicLLMProvider(LLMProvider):
    def __init__(self) -> None:
        self._client: AsyncAnthropic | None = None
        self._model = settings.anthropic_model

    def _get_client(self) -> AsyncAnthropic:
        if self._client is None:
            if not settings.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY is not configured")
            self._client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        return self._client

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = await self._get_client().messages.create(
            model=self._model,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=0.1,
        )
        return response.content[0].text
