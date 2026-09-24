"""Load pre-chunked EU AI Act rows from the Hugging Face dataset."""

import hashlib
from typing import Any

from app.config import settings
from app.ingestion.chunker import Chunk, _split_text, count_tokens


def _row_value(row: dict[str, Any], key: str) -> Any:
    value = row.get(key)
    if value is None:
        return None
    if hasattr(value, "as_py"):
        return value.as_py()
    return value


def _format_article(article_no: int | None) -> str | None:
    if article_no is None:
        return None
    return f"Article {article_no}"


def _format_recital(recital_no: int | None) -> str | None:
    if recital_no is None:
        return None
    return f"Recital {recital_no}"


def _format_annex(annex_no: str | int | None, annex_section: str | int | None = None) -> str | None:
    if annex_no is None:
        return None
    label = f"Annex {annex_no}"
    if annex_section is not None:
        label = f"{label}, point {annex_section}"
    return label


def _content_hash(row_id: str, language: str, text: str, snapshot_version: str | None) -> str:
    payload = f"{row_id}|{language}|{snapshot_version or ''}|{text}"
    return hashlib.sha256(payload.encode()).hexdigest()


def _maybe_split_chunk(chunk: Chunk) -> list[Chunk]:
    """Sub-split only when a dataset row exceeds the configured token budget."""
    token_count = count_tokens(chunk.text)
    if token_count <= settings.chunk_size:
        return [chunk]

    sub_texts = _split_text(chunk.text, settings.chunk_size, settings.chunk_overlap)
    split_chunks: list[Chunk] = []
    for index, sub_text in enumerate(sub_texts):
        split_chunks.append(
            Chunk(
                chunk_id=f"{chunk.chunk_id}__part{index + 1}",
                text=sub_text,
                source_file=chunk.source_file,
                article=chunk.article,
                recital=chunk.recital,
                annex=chunk.annex,
                page=chunk.page,
                language=chunk.language,
                citation_label=chunk.citation_label,
                structure_path=chunk.structure_path,
                source_url=chunk.source_url,
                chunk_type=chunk.chunk_type,
                content_hash=_content_hash(
                    f"{chunk.chunk_id}__part{index + 1}",
                    chunk.language or "",
                    sub_text,
                    None,
                ),
            )
        )
    return split_chunks


def row_to_chunk(row: dict[str, Any], dataset_id: str) -> list[Chunk]:
    row_id = str(_row_value(row, "id") or "")
    language = str(_row_value(row, "language") or "en")
    text = str(_row_value(row, "text") or "").strip()
    if not row_id or not text:
        return []

    article = _format_article(_row_value(row, "article_no"))
    recital = _format_recital(_row_value(row, "recital_no"))
    annex = _format_annex(_row_value(row, "annex_no"), _row_value(row, "annex_section"))
    citation_label = _row_value(row, "citation_label")
    structure_path = _row_value(row, "structure_path")
    source_url = _row_value(row, "source_url")
    chunk_type = _row_value(row, "chunk_type")
    snapshot_version = _row_value(row, "snapshot_version")

    chunk = Chunk(
        chunk_id=row_id,
        text=text,
        source_file=f"hf:{dataset_id}:{language}",
        article=article,
        recital=recital,
        annex=annex,
        language=language,
        citation_label=str(citation_label) if citation_label else None,
        structure_path=str(structure_path) if structure_path else None,
        source_url=str(source_url) if source_url else None,
        chunk_type=str(chunk_type) if chunk_type else None,
        content_hash=_content_hash(row_id, language, text, str(snapshot_version) if snapshot_version else None),
    )
    return _maybe_split_chunk(chunk)


def load_hf_dataset(
    dataset_id: str | None = None,
    languages: list[str] | None = None,
    cache_dir: str | None = None,
) -> list[Chunk]:
    from datasets import load_dataset

    dataset_id = dataset_id or settings.hf_dataset_id
    languages = languages if languages is not None else settings.hf_language_list
    cache_dir = str(settings.resolve_path(cache_dir or settings.hf_dataset_cache_dir))

    dataset = load_dataset(dataset_id, cache_dir=cache_dir)
    split_name = "train" if "train" in dataset else next(iter(dataset.keys()))
    rows = dataset[split_name]

    chunks: list[Chunk] = []
    for row in rows:
        language = str(_row_value(row, "language") or "").lower()
        if languages and language not in languages:
            continue
        chunks.extend(row_to_chunk(row, dataset_id))

    return chunks
