import hashlib
import re
import uuid
from dataclasses import dataclass, field

import tiktoken

from app.config import settings

ARTICLE_PATTERN = re.compile(
    r"^(?:Article|ARTICLE)\s+(\d+[a-z]?(?:\(\d+\))?)",
    re.MULTILINE | re.IGNORECASE,
)
RECITAL_PATTERN = re.compile(
    r"^(?:Recital|RECITAL)\s+\(?(\d+)\)?",
    re.MULTILINE | re.IGNORECASE,
)
ANNEX_PATTERN = re.compile(
    r"^(?:Annex|ANNEX)\s+([IVXLC]+|\d+)",
    re.MULTILINE | re.IGNORECASE,
)


@dataclass
class Chunk:
    chunk_id: str
    text: str
    source_file: str
    article: str | None = None
    recital: str | None = None
    annex: str | None = None
    page: int | None = None
    language: str | None = None
    citation_label: str | None = None
    structure_path: str | None = None
    source_url: str | None = None
    chunk_type: str | None = None
    content_hash: str = field(default="", repr=False)

    def __post_init__(self) -> None:
        if not self.content_hash:
            self.content_hash = hashlib.sha256(self.text.encode()).hexdigest()


def count_tokens(text: str) -> int:
    try:
        return len(tiktoken.get_encoding("cl100k_base").encode(text))
    except Exception:
        # ponytail: word-count fallback; upgrade: always use tiktoken
        return len(text.split())


def chunk_label(chunk: Chunk) -> str:
    if chunk.citation_label:
        return chunk.citation_label
    if chunk.article:
        return chunk.article
    if chunk.recital:
        return chunk.recital
    if chunk.annex:
        return chunk.annex
    return chunk.source_file


def _split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    if not tokens:
        return []
    if len(tokens) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(tokens):
        end = start + chunk_size
        chunks.append(enc.decode(tokens[start:end]))
        if end >= len(tokens):
            break
        start = end - overlap
    return chunks


def _detect_section(text: str) -> tuple[str | None, str | None, str | None]:
    article_match = ARTICLE_PATTERN.search(text)
    recital_match = RECITAL_PATTERN.search(text)
    annex_match = ANNEX_PATTERN.search(text)

    article = f"Article {article_match.group(1)}" if article_match else None
    recital = f"Recital {recital_match.group(1)}" if recital_match else None
    annex = f"Annex {annex_match.group(1)}" if annex_match else None
    return article, recital, annex


def _split_by_legal_structure(text: str) -> list[tuple[str, str | None, str | None, str | None]]:
    """Split text on article/recital/annex boundaries."""
    combined_pattern = re.compile(
        r"(?=(?:Article|ARTICLE|Recital|RECITAL|Annex|ANNEX)\s+)",
        re.MULTILINE,
    )
    parts = combined_pattern.split(text)
    sections: list[tuple[str, str | None, str | None, str | None]] = []

    for part in parts:
        part = part.strip()
        if not part:
            continue
        article, recital, annex = _detect_section(part)
        sections.append((part, article, recital, annex))

    if not sections:
        sections.append((text, None, None, None))

    return sections


def chunk_document(
    text: str,
    source_file: str,
    page: int | None = None,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[Chunk]:
    chunk_size = chunk_size or settings.chunk_size
    chunk_overlap = chunk_overlap or settings.chunk_overlap

    sections = _split_by_legal_structure(text)
    chunks: list[Chunk] = []

    for section_text, article, recital, annex in sections:
        token_count = count_tokens(section_text)

        if token_count <= chunk_size:
            chunks.append(
                Chunk(
                    chunk_id=str(uuid.uuid4()),
                    text=section_text,
                    source_file=source_file,
                    article=article,
                    recital=recital,
                    annex=annex,
                    page=page,
                )
            )
        else:
            sub_texts = _split_text(section_text, chunk_size, chunk_overlap)
            for sub_text in sub_texts:
                sub_article, sub_recital, sub_annex = _detect_section(sub_text)
                chunks.append(
                    Chunk(
                        chunk_id=str(uuid.uuid4()),
                        text=sub_text,
                        source_file=source_file,
                        article=sub_article or article,
                        recital=sub_recital or recital,
                        annex=sub_annex or annex,
                        page=page,
                    )
                )

    return chunks
