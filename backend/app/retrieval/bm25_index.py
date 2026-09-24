import re

from rank_bm25 import BM25Okapi

from app.ingestion.chunker import Chunk


class BM25Index:
    def __init__(self) -> None:
        self._chunks: list[Chunk] = []
        self._bm25: BM25Okapi | None = None

    def _tokenize(self, text: str) -> list[str]:
        return re.findall(r"\w+", text.lower())

    def _rebuild(self) -> None:
        if not self._chunks:
            self._bm25 = None
            return
        corpus = [self._tokenize(c.text) for c in self._chunks]
        self._bm25 = BM25Okapi(corpus)

    def upsert(self, chunks: list[Chunk]) -> None:
        for chunk in chunks:
            self._chunks = [c for c in self._chunks if c.chunk_id != chunk.chunk_id]
            self._chunks.append(chunk)
        self._rebuild()

    def delete(self, chunk_ids: list[str]) -> None:
        if not chunk_ids:
            return
        drop = set(chunk_ids)
        self._chunks = [c for c in self._chunks if c.chunk_id not in drop]
        self._rebuild()

    def query(
        self,
        query_text: str,
        top_k: int = 20,
        language: str | None = None,
    ) -> list[tuple[Chunk, float]]:
        if not self._bm25 or not self._chunks:
            return []

        tokens = self._tokenize(query_text)
        scores = self._bm25.get_scores(tokens)
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)

        results: list[tuple[Chunk, float]] = []
        for idx, score in ranked:
            if score <= 0:
                continue
            chunk = self._chunks[idx]
            if language and chunk.language != language:
                continue
            results.append((chunk, float(score)))
            if len(results) >= top_k:
                break
        return results

    def to_dict(self) -> dict:
        return {
            "chunks": [
                {
                    "chunk_id": c.chunk_id,
                    "text": c.text,
                    "source_file": c.source_file,
                    "article": c.article,
                    "recital": c.recital,
                    "annex": c.annex,
                    "page": c.page,
                    "language": c.language,
                    "citation_label": c.citation_label,
                    "structure_path": c.structure_path,
                    "source_url": c.source_url,
                    "chunk_type": c.chunk_type,
                    "content_hash": c.content_hash,
                }
                for c in self._chunks
            ]
        }

    def load_dict(self, data: dict) -> None:
        """Replace this index's contents while preserving shared references."""
        self._chunks = [
            Chunk(
                chunk_id=raw["chunk_id"],
                text=raw["text"],
                source_file=raw["source_file"],
                article=raw.get("article"),
                recital=raw.get("recital"),
                annex=raw.get("annex"),
                page=raw.get("page"),
                language=raw.get("language"),
                citation_label=raw.get("citation_label"),
                structure_path=raw.get("structure_path"),
                source_url=raw.get("source_url"),
                chunk_type=raw.get("chunk_type"),
                content_hash=raw.get("content_hash", ""),
            )
            for raw in data.get("chunks", [])
        ]
        self._rebuild()

    @classmethod
    def from_dict(cls, data: dict) -> "BM25Index":
        index = cls()
        index.load_dict(data)
        return index
