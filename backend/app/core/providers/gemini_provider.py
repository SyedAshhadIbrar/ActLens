import asyncio

from google import genai
from google.genai import types
from google.genai.errors import ClientError

from app.config import settings
from app.core.providers.base import EmbeddingProvider, LLMProvider

_EMBED_BATCH_SIZE = 20
_MAX_EMBED_RETRIES = 5


def _get_client() -> genai.Client:
    if not settings.google_api_key:
        raise ValueError("GOOGLE_API_KEY is not configured")
    return genai.Client(api_key=settings.google_api_key)


class GeminiLLMProvider(LLMProvider):
    def __init__(self) -> None:
        self._client = _get_client()
        self._model_name = settings.gemini_model

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = await self._client.aio.models.generate_content(
            model=self._model_name,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.1,
            ),
        )
        return response.text or ""


class GeminiEmbeddingProvider(EmbeddingProvider):
    def __init__(self) -> None:
        self._client = _get_client()
        self._model = settings.gemini_embedding_model

    async def _embed_batch(self, texts: list[str]) -> list[list[float]]:
        for attempt in range(_MAX_EMBED_RETRIES):
            try:
                result = await self._client.aio.models.embed_content(
                    model=self._model,
                    contents=texts,
                    config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
                )
                if not result.embeddings:
                    return []
                return [list(embedding.values or []) for embedding in result.embeddings]
            except ClientError as exc:
                if exc.code != 429 or attempt == _MAX_EMBED_RETRIES - 1:
                    raise
                wait_seconds = 35 * (attempt + 1)
                await asyncio.sleep(wait_seconds)
        return []

    async def embed(
        self,
        texts: list[str],
        *,
        input_type: str = "document",
    ) -> list[list[float]]:
        if not texts:
            return []
        embeddings: list[list[float]] = []
        for start in range(0, len(texts), _EMBED_BATCH_SIZE):
            batch = texts[start : start + _EMBED_BATCH_SIZE]
            embeddings.extend(await self._embed_batch(batch))
            await asyncio.sleep(0.5)
        return embeddings
