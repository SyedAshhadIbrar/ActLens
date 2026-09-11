import re

from app.config import settings
from app.ingestion.chunker import Chunk

ARTICLE_QUERY_PATTERN = re.compile(r"article\s+(\d+[a-z]?(?:\(\d+\))?)", re.IGNORECASE)


def reciprocal_rank_fusion(
    result_lists: list[list[tuple[Chunk, float]]],
    k: int = 60,
) -> list[tuple[Chunk, float]]:
    """Fuse multiple ranked lists using Reciprocal Rank Fusion."""
    scores: dict[str, float] = {}
    chunk_map: dict[str, Chunk] = {}

    for results in result_lists:
        for rank, (chunk, _) in enumerate(results):
            chunk_map[chunk.chunk_id] = chunk
            scores[chunk.chunk_id] = scores.get(chunk.chunk_id, 0.0) + 1.0 / (k + rank + 1)

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [(chunk_map[cid], score) for cid, score in ranked]


def _apply_article_boost(
    query: str, results: list[tuple[Chunk, float]]
) -> list[tuple[Chunk, float]]:
    match = ARTICLE_QUERY_PATTERN.search(query)
    if not match:
        return results

    article_num = match.group(1)
    target = f"Article {article_num}"
    structure_target = f"art:{article_num.split('(')[0]}"
    boosted: list[tuple[Chunk, float]] = []
    for chunk, score in results:
        if (
            chunk.article
            and chunk.article.lower().startswith(target.lower())
        ) or (
            chunk.structure_path
            and chunk.structure_path.lower().startswith(structure_target.lower())
        ):
            boosted.append((chunk, score * 2.0))
        else:
            boosted.append((chunk, score))

    boosted.sort(key=lambda x: x[1], reverse=True)
    return boosted


class HybridRetriever:
    def __init__(self, vector_store, bm25_index, embedding_provider) -> None:
        self._vector_store = vector_store
        self._bm25_index = bm25_index
        self._embedding = embedding_provider

    async def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        language: str | None = None,
    ) -> list[tuple[Chunk, float]]:
        top_k = top_k or settings.retrieval_top_k

        query_embedding = (await self._embedding.embed([query], input_type="query"))[0]
        vector_results = self._vector_store.query(
            query_embedding, top_k=top_k, language=language
        )
        bm25_results = self._bm25_index.query(query, top_k=top_k, language=language)

        fused = reciprocal_rank_fusion([vector_results, bm25_results])
        fused = _apply_article_boost(query, fused)
        return fused[:top_k]
