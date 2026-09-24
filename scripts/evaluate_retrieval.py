#!/usr/bin/env python3
"""Run a deterministic retrieval benchmark against the persisted ActLens index."""

import argparse
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))


async def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate ActLens retrieval quality")
    parser.add_argument(
        "--cases",
        type=Path,
        default=ROOT / "evals" / "retrieval_cases.json",
        help="JSON file containing retrieval evaluation cases",
    )
    parser.add_argument("--top-k", type=int, default=5, help="Results evaluated per query")
    parser.add_argument(
        "--min-hit-rate",
        type=float,
        default=0.80,
        help="Exit unsuccessfully when hit rate is below this value",
    )
    parser.add_argument("--output", type=Path, help="Optional JSON report path")
    args = parser.parse_args()

    from app.core.providers.registry import get_embedding_provider
    from app.evaluation.retrieval import evaluate_case, summarize, summarize_by
    from app.ingestion.indexer import Indexer
    from app.ranking.reranker import CrossEncoderReranker
    from app.retrieval.bm25_index import BM25Index
    from app.retrieval.hybrid import HybridRetriever
    from app.retrieval.vector_store import VectorStore

    cases = json.loads(args.cases.read_text(encoding="utf-8"))
    embedding = get_embedding_provider()
    vector_store = VectorStore()
    bm25_index = BM25Index()
    indexer = Indexer(
        embedding,
        vector_store=vector_store,
        bm25_index=bm25_index,
    )
    indexer.load_indexes()
    if not indexer.is_ready():
        print("Index is not ready. Run python scripts/ingest.py first.", file=sys.stderr)
        return 2

    retriever = HybridRetriever(vector_store, bm25_index, embedding)
    reranker = CrossEncoderReranker()

    results = []
    for case in cases:
        candidates = await retriever.retrieve(
            case["query"],
            language=case.get("language", "en"),
        )
        retrieved = reranker.rerank(case["query"], candidates, top_n=args.top_k)
        evaluated = evaluate_case(
            case_id=case["id"],
            query=case["query"],
            language=case.get("language", "en"),
            expected=case["expected"],
            results=retrieved[: args.top_k],
            category=case.get("category", "uncategorized"),
            query_type=case.get("query_type", "natural"),
        )
        results.append(evaluated)
        rank = evaluated.first_relevant_rank or "-"
        print(f"{'PASS' if evaluated.hit else 'FAIL'}  {case['id']:<38} rank={rank}")

    summary = summarize(results)
    try:
        benchmark_path = args.cases.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        benchmark_path = str(args.cases)

    report = {
        "benchmark": benchmark_path,
        "top_k": args.top_k,
        "summary": summary,
        "by_category": summarize_by(results, "category"),
        "by_query_type": summarize_by(results, "query_type"),
        "cases": [result.to_dict() for result in results],
    }
    print(
        f"\nHit@{args.top_k}: {summary['hit_rate']:.1%}  "
        f"MRR: {summary['mrr']:.3f}  "
        f"nDCG@{args.top_k}: {summary['ndcg']:.3f}  "
        f"Cases: {summary['case_count']}"
    )

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Report written to {args.output}")

    return 0 if summary["hit_rate"] >= args.min_hit_rate else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
