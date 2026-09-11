import chromadb

from app.config import settings
from app.ingestion.chunker import Chunk


def _chunk_metadata(chunk: Chunk) -> dict:
    return {
        "source_file": chunk.source_file,
        "article": chunk.article or "",
        "recital": chunk.recital or "",
        "annex": chunk.annex or "",
        "page": chunk.page or 0,
        "content_hash": chunk.content_hash,
        "language": chunk.language or "",
        "citation_label": chunk.citation_label or "",
        "structure_path": chunk.structure_path or "",
        "source_url": chunk.source_url or "",
        "chunk_type": chunk.chunk_type or "",
    }


def _chunk_from_metadata(chunk_id: str, text: str, meta: dict) -> Chunk:
    page = meta.get("page")
    return Chunk(
        chunk_id=chunk_id,
        text=text,
        source_file=meta.get("source_file", ""),
        article=meta.get("article") or None,
        recital=meta.get("recital") or None,
        annex=meta.get("annex") or None,
        page=page if page else None,
        language=meta.get("language") or None,
        citation_label=meta.get("citation_label") or None,
        structure_path=meta.get("structure_path") or None,
        source_url=meta.get("source_url") or None,
        chunk_type=meta.get("chunk_type") or None,
        content_hash=meta.get("content_hash", ""),
    )


class VectorStore:
    def __init__(self) -> None:
        self._client = chromadb.PersistentClient(
            path=str(settings.resolve_path(settings.chroma_persist_dir))
        )
        self._collection = self._client.get_or_create_collection(
            name="eu_ai_act",
            metadata={"hnsw:space": "cosine"},
        )

    def upsert(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        if not chunks:
            return
        self._collection.upsert(
            ids=[c.chunk_id for c in chunks],
            embeddings=embeddings,
            documents=[c.text for c in chunks],
            metadatas=[_chunk_metadata(c) for c in chunks],
        )

    def query(
        self,
        query_embedding: list[float],
        top_k: int = 20,
        language: str | None = None,
    ) -> list[tuple[Chunk, float]]:
        if self._collection.count() == 0:
            return []

        where = {"language": language} if language else None
        n_results = min(top_k, self._collection.count())
        if where:
            n_results = min(top_k * 3, self._collection.count())

        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        chunks: list[tuple[Chunk, float]] = []
        if not results["ids"] or not results["ids"][0]:
            return chunks

        for i, chunk_id in enumerate(results["ids"][0]):
            meta = results["metadatas"][0][i] if results["metadatas"] else {}
            text = results["documents"][0][i] if results["documents"] else ""
            distance = results["distances"][0][i] if results["distances"] else 0.0
            score = 1.0 - distance

            chunk = _chunk_from_metadata(chunk_id, text, meta)
            if language and chunk.language and chunk.language != language:
                continue
            chunks.append((chunk, score))

        return chunks[:top_k]

    def delete(self, chunk_ids: list[str]) -> None:
        if chunk_ids:
            self._collection.delete(ids=chunk_ids)

    def count(self) -> int:
        return self._collection.count()
