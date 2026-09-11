from app.ingestion.chunker import _split_text, count_tokens


def test_split_text_respects_token_chunk_size():
    text = " ".join(["word"] * 2000)
    chunks = _split_text(text, chunk_size=100, overlap=20)
    assert len(chunks) > 1
    assert all(count_tokens(chunk) <= 100 for chunk in chunks)
