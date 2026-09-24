import pytest

from app.evaluation.retrieval import evaluate_case, summarize, summarize_by
from app.ingestion.chunker import Chunk


def _result(article: int) -> tuple[Chunk, float]:
    return (
        Chunk(
            chunk_id=f"article-{article}",
            text=f"Article {article} text",
            source_file="test",
            article=f"Article {article}",
            language="en",
            citation_label=f"Art. {article} AI Act",
            structure_path=f"art:{article}",
        ),
        1.0,
    )


def test_evaluate_case_finds_first_relevant_rank():
    result = evaluate_case(
        case_id="risk",
        query="risk management",
        language="en",
        expected=["art:9"],
        results=[_result(6), _result(9)],
    )

    assert result.hit is True
    assert result.first_relevant_rank == 2
    assert result.reciprocal_rank == 0.5
    assert result.ndcg == pytest.approx(1 / 1.584962500721156)


def test_summarize_reports_hit_rate_and_mrr():
    hit = evaluate_case(
        case_id="hit",
        query="risk",
        language="en",
        expected=["art:9"],
        results=[_result(9)],
    )
    miss = evaluate_case(
        case_id="miss",
        query="oversight",
        language="en",
        expected=["art:14"],
        results=[_result(9)],
    )

    summary = summarize([hit, miss])

    assert summary["case_count"] == 2
    assert summary["hit_rate"] == pytest.approx(0.5)
    assert summary["mrr"] == pytest.approx(0.5)
    assert summary["ndcg"] == pytest.approx(0.5)


def test_canonical_article_match_does_not_match_longer_article_number():
    result = evaluate_case(
        case_id="prohibited",
        query="prohibited practices",
        language="en",
        expected=["art:5"],
        results=[_result(50)],
    )

    assert result.hit is False


def test_summarize_by_groups_results_for_slice_analysis():
    natural = evaluate_case(
        case_id="natural",
        query="risk management",
        language="en",
        expected=["art:9"],
        results=[_result(9)],
        category="high-risk",
        query_type="natural",
    )
    scenario = evaluate_case(
        case_id="scenario",
        query="a deployer uses a system",
        language="en",
        expected=["art:26"],
        results=[],
        category="operators",
        query_type="scenario",
    )

    by_type = summarize_by([natural, scenario], "query_type")

    assert by_type["natural"]["hit_rate"] == 1.0
    assert by_type["scenario"]["hit_rate"] == 0.0
