from openai import AsyncOpenAI

from app.config import settings
from app.core.providers.base import EmbeddingProvider, LLMProvider


class OpenAILLMProvider(LLMProvider):
    def __init__(self) -> None:
        self._client: AsyncOpenAI | None = None
        self._model = settings.openai_model

    def _get_client(self) -> AsyncOpenAI:
        if self._client is None:
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY is not configured")
            self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        return self._client

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = await self._get_client().chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
        )
        return response.choices[0].message.content or ""


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self) -> None:
        self._client: AsyncOpenAI | None = None
        self._model = settings.openai_embedding_model

    def _get_client(self) -> AsyncOpenAI:
        if self._client is None:
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY is not configured")
            self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        return self._client

    async def embed(self, texts: list[str], *, input_type: str = "document") -> list[list[float]]:
        if not texts:
            return []
        response = await self._get_client().embeddings.create(
            model=self._model,
            input=texts,
        )
        return [item.embedding for item in response.data]
