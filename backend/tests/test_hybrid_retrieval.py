from app.ingestion.chunker import Chunk
from app.retrieval.hybrid import _apply_article_boost, reciprocal_rank_fusion


def _chunk(article: int) -> Chunk:
    return Chunk(
        chunk_id=f"article-{article}",
        text=f"Article {article} text",
        source_file="test",
        article=f"Article {article}",
        language="en",
        citation_label=f"Art. {article} AI Act",
        structure_path=f"art:{article}",
    )


def test_reciprocal_rank_fusion_rewards_cross_retriever_agreement():
    article_9 = _chunk(9)
    article_14 = _chunk(14)
    article_26 = _chunk(26)

    fused = reciprocal_rank_fusion(
        [
            [(article_9, 0.9), (article_14, 0.8)],
            [(article_26, 4.0), (article_9, 3.0)],
        ]
    )

    assert fused[0][0].chunk_id == "article-9"


def test_article_query_boost_prioritizes_requested_article():
    article_6 = _chunk(6)
    article_9 = _chunk(9)

    boosted = _apply_article_boost(
        "Explain Article 9 risk management",
        [(article_6, 0.9), (article_9, 0.5)],
    )

    assert boosted[0][0].chunk_id == "article-9"
    assert boosted[0][1] == 1.0
