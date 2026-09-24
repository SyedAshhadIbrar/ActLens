import json
import pickle
from datetime import datetime, timezone

from app.config import settings
from app.core.providers.base import EmbeddingProvider
from app.ingestion.chunker import Chunk
from app.ingestion.hf_dataset import load_hf_dataset
from app.ingestion.loader import LoadedDocument, load_documents
from app.retrieval.bm25_index import BM25Index
from app.retrieval.vector_store import VectorStore


class Indexer:
    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore | None = None,
        bm25_index: BM25Index | None = None,
    ) -> None:
        self._embedding = embedding_provider
        self._vector_store = vector_store or VectorStore()
        self._bm25_index = bm25_index or BM25Index()
        self._manifest_path = settings.resolve_path(settings.manifest_path)

    def _load_manifest(self) -> dict:
        if self._manifest_path.exists():
            return json.loads(self._manifest_path.read_text(encoding="utf-8"))
        return {"chunks": {}, "documents": {}}

    def _save_manifest(self, manifest: dict) -> None:
        self._manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self._manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    def _persist_bm25(self) -> None:
        bm25_path = settings.resolve_path(settings.bm25_index_path)
        bm25_path.parent.mkdir(parents=True, exist_ok=True)
        with open(bm25_path, "wb") as f:
            pickle.dump(self._bm25_index.to_dict(), f)

    def _load_bm25(self) -> None:
        bm25_path = settings.resolve_path(settings.bm25_index_path)
        if bm25_path.exists():
            with open(bm25_path, "rb") as f:
                data = pickle.load(f)
            self._bm25_index.load_dict(data)

    async def ingest(
        self,
        source: str | None = None,
        languages: list[str] | None = None,
    ) -> dict:
        source = (source or settings.data_source).lower()
        self._load_bm25()
        manifest = self._load_manifest()
        stats = {
            "files_processed": 0,
            "chunks_added": 0,
            "chunks_updated": 0,
            "chunks_unchanged": 0,
        }

        if source in ("hf", "both"):
            await self._ingest_hf_dataset(manifest, stats, languages=languages)
        if source in ("files", "both"):
            directory = str(settings.resolve_path(settings.data_raw_dir))
            documents = load_documents(directory)
            for doc in documents:
                stats["files_processed"] += 1
                await self._ingest_document(doc, manifest, stats)

        self._save_manifest(manifest)
        self._persist_bm25()
        return stats

    async def _ingest_hf_dataset(
        self,
        manifest: dict,
        stats: dict,
        languages: list[str] | None = None,
    ) -> None:
        chunks = load_hf_dataset(languages=languages)
        if not chunks:
            return

        stats["files_processed"] += 1
        await self._ingest_chunks(
            chunks,
            manifest,
            stats,
            source_name=f"hf:{settings.hf_dataset_id}",
        )

    async def _ingest_chunks(
        self,
        all_chunks: list[Chunk],
        manifest: dict,
        stats: dict,
        source_name: str,
    ) -> None:
        new_chunks: list[Chunk] = []
        updated_chunks: list[Chunk] = []
        stale_ids: list[str] = []

        for chunk in all_chunks:
            existing = manifest["chunks"].get(chunk.content_hash)
            if existing:
                stats["chunks_unchanged"] += 1
                chunk.chunk_id = existing["chunk_id"]
            elif chunk.content_hash in [
                v.get("content_hash") for v in manifest["chunks"].values()
            ]:
                stats["chunks_unchanged"] += 1
            else:
                old_entry = None
                for key, val in manifest["chunks"].items():
                    if (
                        val.get("source_file") == chunk.source_file
                        and val.get("text", "")[:100] == chunk.text[:100]
                    ):
                        old_entry = key
                        break

                if old_entry:
                    stale_ids.append(manifest["chunks"][old_entry]["chunk_id"])
                    updated_chunks.append(chunk)
                    stats["chunks_updated"] += 1
                    del manifest["chunks"][old_entry]
                else:
                    new_chunks.append(chunk)
                    stats["chunks_added"] += 1

                manifest["chunks"][chunk.content_hash] = {
                    "chunk_id": chunk.chunk_id,
                    "source_file": chunk.source_file,
                    "content_hash": chunk.content_hash,
                    "text": chunk.text[:200],
                    "article": chunk.article,
                    "recital": chunk.recital,
                    "annex": chunk.annex,
                    "language": chunk.language,
                    "citation_label": chunk.citation_label,
                    "structure_path": chunk.structure_path,
                    "source_url": chunk.source_url,
                }

        if stale_ids:
            self._vector_store.delete(stale_ids)
            self._bm25_index.delete(stale_ids)

        chunks_to_embed = new_chunks + updated_chunks
        if chunks_to_embed:
            texts = [c.text for c in chunks_to_embed]
            embeddings = await self._embedding.embed(texts)
            self._vector_store.upsert(chunks_to_embed, embeddings)
            self._bm25_index.upsert(chunks_to_embed)

        manifest["documents"][source_name] = {
            "chunk_count": len(all_chunks),
            "last_indexed": datetime.now(timezone.utc).isoformat(),
        }

    async def _ingest_document(
        self, doc: LoadedDocument, manifest: dict, stats: dict
    ) -> None:
        from app.ingestion.chunker import chunk_document

        if doc.pages:
            all_chunks: list[Chunk] = []
            for i, page_text in enumerate(doc.pages):
                if page_text.strip():
                    all_chunks.extend(
                        chunk_document(page_text, doc.source_file, page=i + 1)
                    )
        else:
            all_chunks = chunk_document(doc.text, doc.source_file)

        await self._ingest_chunks(all_chunks, manifest, stats, source_name=doc.source_file)

    def get_document_list(self) -> tuple[list[dict], int]:
        manifest = self._load_manifest()
        documents = [
            {
                "source_file": name,
                "chunk_count": info["chunk_count"],
                "last_indexed": info.get("last_indexed"),
            }
            for name, info in manifest.get("documents", {}).items()
        ]
        total = len(manifest.get("chunks", {}))
        return documents, total

    def load_indexes(self) -> None:
        """Load persisted BM25 index from disk."""
        self._load_bm25()

    def is_ready(self) -> bool:
        manifest = self._load_manifest()
        # ponytail: manifest alone is not enough; vectors must exist on disk
        return len(manifest.get("chunks", {})) > 0 and self._vector_store.count() > 0

    def get_chunk_count(self) -> int:
        manifest = self._load_manifest()
        return len(manifest.get("chunks", {}))
