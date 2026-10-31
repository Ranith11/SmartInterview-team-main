"""
SmartInterview Paper Evidence - Task 1 Retrieval Ablation
Runs evaluation over data/evaluation/golden_evaluation_dataset.json (33 queries)
for all configurations requested:
  a) dense only
  b) BM25 only
  c) graph only
  d) dense + BM25 (no graph) [RRF and Weighted]
  e) dense + BM25 + graph, RRF, without reranker
  f) full pipeline:
     f1) RRF + SemanticEmbeddingReranker (default repo reranker)
     f2) RRF + CrossEncoderReranker (cross-encoder/ms-marco-MiniLM-L-6-v2)
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.services.question_service import (
    _init_rag,
    get_embedding_model,
    get_chroma_collection,
    build_rag_query,
)
from app.rag.vector_retriever import VectorRetriever
from app.rag.keyword_retriever import KeywordRetriever
from app.rag.graph_retriever import GraphRetriever
from app.rag.hybrid_retriever import HybridRetriever
from app.rag.reranker import get_reranker, CrossEncoderReranker, SemanticEmbeddingReranker
from app.rag.graph_store import get_graph_store
from app.rag.evaluation_metrics import (
    evaluate_query_run,
    aggregate_evaluation_results,
    QueryEvaluationResult,
)

def run_eval_for_retriever(
    name: str,
    retriever_fn,
    golden_dataset: list,
    top_k: int = 5,
) -> Dict[str, Any]:
    print(f"\n--- Running evaluation: {name} ---")
    query_evals: List[QueryEvaluationResult] = []
    per_query_records: List[Dict[str, Any]] = []
    failed_hit1_queries: List[str] = []

    for item in golden_dataset:
        q_id = item["query_id"]
        q_text = item["query"]
        domain = item["domain"]
        concept = item["concept"]
        bloom_level = item.get("bloom_level")
        expected_chunk_ids = set(item.get("expected_chunk_ids", []))
        expected_prereqs = item.get("expected_prerequisites", [])

        start_time = time.perf_counter()
        results = retriever_fn(q_text, domain, concept, bloom_level, top_k)
        latency_ms = (time.perf_counter() - start_time) * 1000.0

        q_eval = evaluate_query_run(
            query_id=q_id,
            query=q_text,
            results=results,
            ground_truth_chunk_ids=expected_chunk_ids,
            target_prerequisites=expected_prereqs,
            latency_ms=latency_ms,
        )
        query_evals.append(q_eval)

        if q_eval.hit_1 == 0.0:
            failed_hit1_queries.append(q_id)

        per_query_records.append({
            "query_id": q_id,
            "query": q_text,
            "concept": concept,
            "hit_1": q_eval.hit_1,
            "hit_3": q_eval.hit_3,
            "hit_5": q_eval.hit_5,
            "recall_5": q_eval.recall_5,
            "mrr": q_eval.mrr,
            "latency_ms": latency_ms,
            "retrieved_chunk_ids": [r.chunk_id for r in results[:top_k]],
            "ground_truth_chunk_ids": list(expected_chunk_ids),
        })

    agg = aggregate_evaluation_results(query_evals)
    summary = {
        "name": name,
        "hit_at_1": agg.hit_at_1,
        "hit_at_3": agg.hit_at_3,
        "hit_at_5": agg.hit_at_5,
        "recall_at_5": agg.recall_at_5,
        "precision_at_5": agg.precision_at_5,
        "mrr": agg.mrr,
        "mean_latency_ms": agg.latency["mean"],
        "median_latency_ms": agg.latency["p50"],
        "p95_latency_ms": agg.latency["p95"],
        "failed_hit1_queries": failed_hit1_queries,
        "total_failed_hit1": len(failed_hit1_queries),
    }

    print(f"Results for {name}:")
    print(f"  Hit@1: {agg.hit_at_1}%")
    print(f"  Hit@3: {agg.hit_at_3}%")
    print(f"  Recall@5: {agg.recall_at_5}%")
    print(f"  MRR: {agg.mrr}")
    print(f"  Mean Latency: {agg.latency['mean']} ms")
    print(f"  Failed Hit@1 ({len(failed_hit1_queries)}): {failed_hit1_queries}")

    return {
        "summary": summary,
        "per_query": per_query_records,
    }


def main():
    print("Initializing components for Task 1 ablation...")
    _init_rag()
    embedding_model = get_embedding_model()
    chroma = get_chroma_collection()
    graph_store = get_graph_store()

    # Base retrievers
    vec_retriever = VectorRetriever(
        embedding_model=embedding_model,
        collection=chroma,
        build_rag_query_fn=build_rag_query,
    )
    kw_retriever = KeywordRetriever()
    gr_retriever = GraphRetriever(graph_store=graph_store)

    # Hybrid Dense + BM25 (no graph)
    hybrid_dense_bm25_rrf = HybridRetriever(
        vector_retriever=vec_retriever,
        keyword_retriever=kw_retriever,
        graph_retriever=None,
        weights={"vector": 0.60, "keyword": 0.40},
        fusion_method="rrf",
        fetch_k=10,
    )
    hybrid_dense_bm25_weighted = HybridRetriever(
        vector_retriever=vec_retriever,
        keyword_retriever=kw_retriever,
        graph_retriever=None,
        weights={"vector": 0.60, "keyword": 0.40},
        fusion_method="weighted",
        fetch_k=10,
    )

    # Tri-hybrid (Dense + BM25 + Graph)
    hybrid_tri_rrf = HybridRetriever(
        vector_retriever=vec_retriever,
        keyword_retriever=kw_retriever,
        graph_retriever=gr_retriever,
        weights={"vector": 0.40, "keyword": 0.25, "graph": 0.35},
        fusion_method="rrf",
        fetch_k=10,
    )

    # Rerankers
    semantic_reranker = SemanticEmbeddingReranker(embedding_model=embedding_model)
    cross_encoder_reranker = CrossEncoderReranker(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2")

    # Load golden dataset
    golden_path = PROJECT_ROOT / "data" / "evaluation" / "golden_evaluation_dataset.json"
    with open(golden_path, "r", encoding="utf-8") as f:
        golden_dataset = json.load(f)

    print(f"Loaded {len(golden_dataset)} golden evaluation queries.")

    # Warmups
    print("Warming up retrievers and rerankers...")
    _ = vec_retriever.retrieve("warmup", "dns", ["cn"], top_k=1)
    _ = kw_retriever.retrieve("warmup", "dns", ["cn"], top_k=1)
    _ = gr_retriever.retrieve("warmup", "dns", ["cn"], top_k=1)
    _ = hybrid_tri_rrf.retrieve("warmup", "dns", ["cn"], top_k=5)
    _w_res = vec_retriever.retrieve("warmup", "dns", ["cn"], top_k=3)
    _ = semantic_reranker.rerank("warmup", _w_res, top_k=2)
    _ = cross_encoder_reranker.rerank("warmup", _w_res, top_k=2)

    all_results = {}

    # a) dense only
    all_results["a_dense_only"] = run_eval_for_retriever(
        "a) Dense Only",
        lambda q, d, c, b, k: vec_retriever.retrieve(query=q, skill=c, domains=[d], top_k=k),
        golden_dataset,
        top_k=5,
    )

    # b) BM25 only
    all_results["b_bm25_only"] = run_eval_for_retriever(
        "b) BM25 Only",
        lambda q, d, c, b, k: kw_retriever.retrieve(query=q, skill=c, domains=[d], top_k=k),
        golden_dataset,
        top_k=5,
    )

    # c) graph only
    all_results["c_graph_only"] = run_eval_for_retriever(
        "c) Graph Only",
        lambda q, d, c, b, k: gr_retriever.retrieve(query=q, skill=c, domains=[d], concept=c, bloom_level=b, top_k=k),
        golden_dataset,
        top_k=5,
    )

    # d) dense + BM25 (no graph) - RRF
    all_results["d_dense_bm25_rrf"] = run_eval_for_retriever(
        "d) Dense + BM25 (No Graph) [RRF]",
        lambda q, d, c, b, k: hybrid_dense_bm25_rrf.retrieve(query=q, skill=c, domains=[d], top_k=k, fusion_method="rrf"),
        golden_dataset,
        top_k=5,
    )

    # d2) dense + BM25 (no graph) - Weighted
    all_results["d2_dense_bm25_weighted"] = run_eval_for_retriever(
        "d2) Dense + BM25 (No Graph) [Weighted]",
        lambda q, d, c, b, k: hybrid_dense_bm25_weighted.retrieve(query=q, skill=c, domains=[d], top_k=k, fusion_method="weighted"),
        golden_dataset,
        top_k=5,
    )

    # e) dense + BM25 + graph, RRF, WITHOUT cross-encoder reranker
    all_results["e_dense_bm25_graph_rrf_no_reranker"] = run_eval_for_retriever(
        "e) Dense + BM25 + Graph (RRF, No Reranker)",
        lambda q, d, c, b, k: hybrid_tri_rrf.retrieve(query=q, skill=c, domains=[d], concept=c, bloom_level=b, top_k=k, fusion_method="rrf"),
        golden_dataset,
        top_k=5,
    )

    # f1) full pipeline (RRF + SemanticEmbeddingReranker - default in codebase)
    def full_pipeline_semantic(q, d, c, b, k):
        candidates = hybrid_tri_rrf.retrieve(query=q, skill=c, domains=[d], concept=c, bloom_level=b, top_k=10, fusion_method="rrf")
        return semantic_reranker.rerank(query=q, results=candidates, top_k=k)

    all_results["f1_full_pipeline_semantic_reranker"] = run_eval_for_retriever(
        "f1) Full Pipeline (RRF + SemanticEmbeddingReranker)",
        full_pipeline_semantic,
        golden_dataset,
        top_k=5,
    )

    # f2) full pipeline (RRF + CrossEncoderReranker)
    def full_pipeline_cross_encoder(q, d, c, b, k):
        candidates = hybrid_tri_rrf.retrieve(query=q, skill=c, domains=[d], concept=c, bloom_level=b, top_k=10, fusion_method="rrf")
        return cross_encoder_reranker.rerank(query=q, results=candidates, top_k=k)

    all_results["f2_full_pipeline_cross_encoder"] = run_eval_for_retriever(
        "f2) Full Pipeline (RRF + CrossEncoderReranker)",
        full_pipeline_cross_encoder,
        golden_dataset,
        top_k=5,
    )

    out_json = PROJECT_ROOT / "paper_eval" / "task1_ablation_results.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    print(f"\nSaved Task 1 ablation results to {out_json}")

if __name__ == "__main__":
    main()
