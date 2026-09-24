from app.ingestion.chunker import Chunk
from app.processing.context import deduplicate_chunks, prepare_context


def _chunk(chunk_id: str, text: str, structure_path: str) -> Chunk:
    return Chunk(
        chunk_id=chunk_id,
        text=text,
        source_file="test",
        article="Article 9",
        language="en",
        citation_label="Art. 9 AI Act",
        structure_path=structure_path,
    )


def test_deduplicate_chunks_removes_duplicate_legal_structure():
    first = _chunk("one", "Risk management requirement.", "art:9/par:1")
    duplicate = _chunk("two", "Different copy of the requirement.", "art:9/par:1")

    deduplicated = deduplicate_chunks([(first, 1.0), (duplicate, 0.8)])

    assert [chunk.chunk_id for chunk, _ in deduplicated] == ["one"]


def test_prepare_context_respects_token_budget():
    short = _chunk("short", "Risk management.", "art:9/par:1")
    long = _chunk("long", "word " * 200, "art:9/par:2")

    context, selected = prepare_context([(short, 1.0), (long, 0.9)], max_tokens=20)

    assert [chunk.chunk_id for chunk in selected] == ["short"]
    assert "Risk management." in context
    assert "word word" not in context
