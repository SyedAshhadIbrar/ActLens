from dataclasses import asdict, dataclass
from math import log2

from app.ingestion.chunker import Chunk


@dataclass(frozen=True)
class RetrievalCaseResult:
    case_id: str
    query: str
    language: str
    expected: list[str]
    first_relevant_rank: int | None
    retrieved_labels: list[str]
    category: str = "uncategorized"
    query_type: str = "natural"

    @property
    def hit(self) -> bool:
        return self.first_relevant_rank is not None

    @property
    def reciprocal_rank(self) -> float:
        if self.first_relevant_rank is None:
            return 0.0
        return 1.0 / self.first_relevant_rank

    @property
    def ndcg(self) -> float:
        if self.first_relevant_rank is None:
            return 0.0
        return 1.0 / log2(self.first_relevant_rank + 1)

    def to_dict(self) -> dict:
        return {
            **asdict(self),
            "hit": self.hit,
            "reciprocal_rank": self.reciprocal_rank,
            "ndcg": self.ndcg,
        }


def _searchable_metadata(chunk: Chunk) -> str:
    values = (
        chunk.citation_label,
        chunk.structure_path,
        chunk.article,
        chunk.recital,
        chunk.annex,
    )
    return " | ".join(value.lower() for value in values if value)


def _matches_expected(chunk: Chunk, expected: str) -> bool:
    expected = expected.strip().lower()
    structure_path = (chunk.structure_path or "").lower()
    if expected.startswith(("art:", "rec:", "annex:")):
        return structure_path == expected or structure_path.startswith(f"{expected}/")
    return expected in _searchable_metadata(chunk)


def evaluate_case(
    *,
    case_id: str,
    query: str,
    language: str,
    expected: list[str],
    results: list[tuple[Chunk, float]],
    category: str = "uncategorized",
    query_type: str = "natural",
) -> RetrievalCaseResult:
    expected_normalized = [value.strip().lower() for value in expected if value.strip()]
    first_relevant_rank = None

    for rank, (chunk, _) in enumerate(results, start=1):
        if any(_matches_expected(chunk, value) for value in expected_normalized):
            first_relevant_rank = rank
            break

    labels = [
        chunk.citation_label
        or chunk.structure_path
        or chunk.article
        or chunk.recital
        or chunk.chunk_id
        for chunk, _ in results
    ]
    return RetrievalCaseResult(
        case_id=case_id,
        query=query,
        language=language,
        expected=expected,
        first_relevant_rank=first_relevant_rank,
        retrieved_labels=labels,
        category=category,
        query_type=query_type,
    )


def summarize(results: list[RetrievalCaseResult]) -> dict:
    if not results:
        return {"case_count": 0, "hit_rate": 0.0, "mrr": 0.0, "ndcg": 0.0}

    return {
        "case_count": len(results),
        "hit_rate": sum(result.hit for result in results) / len(results),
        "mrr": sum(result.reciprocal_rank for result in results) / len(results),
        "ndcg": sum(result.ndcg for result in results) / len(results),
    }


def summarize_by(results: list[RetrievalCaseResult], field: str) -> dict[str, dict]:
    grouped: dict[str, list[RetrievalCaseResult]] = {}
    for result in results:
        key = str(getattr(result, field))
        grouped.setdefault(key, []).append(result)
    return {key: summarize(group) for key, group in sorted(grouped.items())}
