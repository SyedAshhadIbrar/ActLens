from app.config import settings
from app.ingestion.chunker import Chunk


class CrossEncoderReranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2") -> None:
        self._model_name = model_name
        self._model = None

    def _load_model(self):
        if self._model is None:
            from sentence_transformers import CrossEncoder

            self._model = CrossEncoder(self._model_name)
        return self._model

    def rerank(
        self,
        query: str,
        chunks: list[tuple[Chunk, float]],
        top_n: int | None = None,
    ) -> list[tuple[Chunk, float]]:
        top_n = top_n or settings.rerank_top_n
        if not chunks:
            return []

        model = self._load_model()
        pairs = [(query, chunk.text) for chunk, _ in chunks]
        scores = model.predict(pairs)

        scored = [(chunks[i][0], float(scores[i])) for i in range(len(chunks))]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_n]
