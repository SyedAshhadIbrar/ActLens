import asyncio

from sentence_transformers import SentenceTransformer

from app.config import settings
from app.core.providers.base import EmbeddingProvider, EmbedInputType


class HFEmbeddingProvider(EmbeddingProvider):
    """Local embeddings via Hugging Face sentence-transformers (no API key)."""

    def __init__(self) -> None:
        self._model_name = settings.hf_embedding_model
        self._model: SentenceTransformer | None = None

    def _load_model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self._model_name)
        return self._model

    def _prepare_texts(self, texts: list[str], input_type: EmbedInputType) -> list[str]:
        if "e5" not in self._model_name.lower():
            return texts
        prefix = "query: " if input_type == "query" else "passage: "
        return [f"{prefix}{text}" for text in texts]

    async def embed(
        self,
        texts: list[str],
        *,
        input_type: EmbedInputType = "document",
    ) -> list[list[float]]:
        if not texts:
            return []
        model = self._load_model()
        prepared = self._prepare_texts(texts, input_type)
        vectors = await asyncio.to_thread(
            model.encode,
            prepared,
            normalize_embeddings=True,
            show_progress_bar=len(prepared) > 50,
        )
        return vectors.tolist()
