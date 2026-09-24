from app.ingestion.chunker import Chunk
from app.retrieval.bm25_index import BM25Index


def _chunk(chunk_id: str, text: str) -> Chunk:
    return Chunk(
        chunk_id=chunk_id,
        text=text,
        source_file="test",
        article="Article 9",
        language="en",
        citation_label="Art. 9 AI Act",
        structure_path="art:9",
    )


def test_load_dict_updates_existing_shared_index():
    persisted = BM25Index()
    persisted.upsert(
        [
            _chunk("risk", "risk management system lifecycle"),
            _chunk("oversight", "human oversight controls"),
            _chunk("transparency", "transparency instructions"),
        ]
    )

    shared_index = BM25Index()
    shared_reference = shared_index
    shared_index.load_dict(persisted.to_dict())

    results = shared_reference.query("risk management", language="en")

    assert shared_reference is shared_index
    assert [chunk.chunk_id for chunk, _ in results] == ["risk"]
