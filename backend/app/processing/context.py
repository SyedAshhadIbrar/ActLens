from app.config import settings
from app.ingestion.chunker import Chunk, chunk_label, count_tokens


def _article_sort_key(chunk: Chunk) -> tuple:
    def parse_num(label: str | None) -> int:
        if not label:
            return 9999
        nums = "".join(c for c in label if c.isdigit())
        return int(nums) if nums else 9999

    return (
        0 if chunk.article else (1 if chunk.recital else 2),
        parse_num(chunk.article or chunk.recital or chunk.annex),
    )


def deduplicate_chunks(chunks: list[tuple[Chunk, float]]) -> list[tuple[Chunk, float]]:
    seen_hashes: set[str] = set()
    seen_structure_paths: set[str] = set()
    seen_prefixes: set[str] = set()
    deduped: list[tuple[Chunk, float]] = []

    for chunk, score in chunks:
        if chunk.content_hash in seen_hashes:
            continue
        if chunk.structure_path and chunk.structure_path in seen_structure_paths:
            continue
        prefix = chunk.text[:200]
        if prefix in seen_prefixes:
            continue
        seen_hashes.add(chunk.content_hash)
        if chunk.structure_path:
            seen_structure_paths.add(chunk.structure_path)
        seen_prefixes.add(prefix)
        deduped.append((chunk, score))

    return deduped


def prepare_context(
    chunks: list[tuple[Chunk, float]],
    max_tokens: int | None = None,
) -> tuple[str, list[Chunk]]:
    max_tokens = max_tokens or settings.max_context_tokens

    deduped = deduplicate_chunks(chunks)
    deduped.sort(key=lambda x: _article_sort_key(x[0]))

    context_parts: list[str] = []
    selected: list[Chunk] = []
    total_tokens = 0

    for chunk, score in deduped:
        entry = f"[{chunk_label(chunk)}]\n{chunk.text}"
        entry_tokens = count_tokens(entry)

        if total_tokens + entry_tokens > max_tokens:
            break

        context_parts.append(entry)
        selected.append(chunk)
        total_tokens += entry_tokens

    return "\n\n---\n\n".join(context_parts), selected
