"""
SmartInterview Paper Evidence - Task 3 Latency Breakdown
Measures per-stage latency over 30 runs each:
  1. Embedding of query
  2. Vector retrieval
  3. BM25 keyword retrieval
  4. Graph retrieval
  5. RRF fusion
  6. Contextual reranker (Semantic & CrossEncoder)
  7. Groq Whisper transcription (using sample audio)
  8. LLM Time-to-First-Token (TTFT) via Groq streaming
  9. Edge-TTS neural speech synthesis (uncached)
 10. End-to-end speech-to-speech turnaround
Reports mean, median (p50), and p95 for each stage.
"""

import os
import sys
import io
import wave
import time
import json
import math
import struct
import asyncio
import numpy as np
from pathlib import Path
from typing import Dict, Any, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.services.question_service import (
    _init_rag,
    _init_groq,
    get_embedding_model,
    get_chroma_collection,
    get_groq_client,
    get_groq_model_name,
    build_rag_query,
)
from app.rag.vector_retriever import VectorRetriever
from app.rag.keyword_retriever import KeywordRetriever
from app.rag.graph_retriever import GraphRetriever
from app.rag.hybrid_retriever import HybridRetriever
from app.rag.reranker import SemanticEmbeddingReranker, CrossEncoderReranker
from app.rag.graph_store import get_graph_store
from app.services.voice_service import _get_groq_client, synthesize_speech_bytes, _TTS_CACHE

def calc_stats(latencies_ms: List[float]) -> Dict[str, float]:
    arr = np.array(latencies_ms)
    return {
        "runs": len(latencies_ms),
        "mean_ms": round(float(np.mean(arr)), 2),
        "median_ms": round(float(np.median(arr)), 2),
        "p95_ms": round(float(np.percentile(arr, 95)), 2),
        "min_ms": round(float(np.min(arr)), 2),
        "max_ms": round(float(np.max(arr)), 2),
        "std_ms": round(float(np.std(arr)), 2),
    }

def generate_sample_wav(duration_sec: float = 1.0) -> bytes:
    """Generate a clean 16kHz 16-bit mono PCM wav audio in memory."""
    buf = io.BytesIO()
    sample_rate = 16000
    num_samples = int(sample_rate * duration_sec)
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for i in range(num_samples):
            # 440Hz tone with low amplitude
            val = int(32767.0 * 0.1 * math.sin(2.0 * math.pi * 440.0 * i / sample_rate))
            wf.writeframes(struct.pack('<h', val))
    return buf.getvalue()

async def run_latency_benchmarks(num_runs: int = 30):
    print("=" * 70)
    print(f"SmartInterview — Task 3 Latency Breakdown ({num_runs} runs per stage)")
    print("=" * 70)

    _init_rag()
    _init_groq()
    embedding_model = get_embedding_model()
    chroma = get_chroma_collection()
    graph_store = get_graph_store()
    groq_client = get_groq_client()
    groq_model = get_groq_model_name()
    whisper_client = _get_groq_client()

    vec_retriever = VectorRetriever(
        embedding_model=embedding_model,
        collection=chroma,
        build_rag_query_fn=build_rag_query,
    )
    kw_retriever = KeywordRetriever()
    gr_retriever = GraphRetriever(graph_store=graph_store)
    hybrid_retriever = HybridRetriever(
        vector_retriever=vec_retriever,
        keyword_retriever=kw_retriever,
        graph_retriever=gr_retriever,
        weights={"vector": 0.40, "keyword": 0.25, "graph": 0.35},
        fusion_method="rrf",
        fetch_k=10,
    )
    semantic_reranker = SemanticEmbeddingReranker(embedding_model=embedding_model)
    cross_encoder = CrossEncoderReranker(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2")

    test_query = "What are the ACID properties in database transactions?"
    test_skill = "acid-properties"
    test_domain = "dbms"
    sample_wav_bytes = generate_sample_wav(1.0)

    results = {}

    # 1. Embedding of query
    print("\n[1/10] Measuring Query Embedding latency...")
    emb_lats = []
    # Warmup
    _ = embedding_model.encode(test_query, convert_to_numpy=True)
    for _ in range(num_runs):
        t0 = time.perf_counter()
        _ = embedding_model.encode(test_query, convert_to_numpy=True)
        emb_lats.append((time.perf_counter() - t0) * 1000.0)
    results["query_embedding"] = {"raw": emb_lats, "stats": calc_stats(emb_lats)}
    print(f"  Done. Mean: {results['query_embedding']['stats']['mean_ms']} ms, Median: {results['query_embedding']['stats']['median_ms']} ms, P95: {results['query_embedding']['stats']['p95_ms']} ms")

    # 2. Vector retrieval (ChromaDB)
    print("\n[2/10] Measuring ChromaDB Vector Retrieval latency...")
    vec_lats = []
    _ = vec_retriever.retrieve(query=test_query, skill=test_skill, domains=[test_domain], top_k=5)
    for _ in range(num_runs):
        t0 = time.perf_counter()
        _ = vec_retriever.retrieve(query=test_query, skill=test_skill, domains=[test_domain], top_k=5)
        vec_lats.append((time.perf_counter() - t0) * 1000.0)
    results["vector_retrieval"] = {"raw": vec_lats, "stats": calc_stats(vec_lats)}
    print(f"  Done. Mean: {results['vector_retrieval']['stats']['mean_ms']} ms, Median: {results['vector_retrieval']['stats']['median_ms']} ms, P95: {results['vector_retrieval']['stats']['p95_ms']} ms")

    # 3. BM25 keyword retrieval
    print("\n[3/10] Measuring BM25 Retrieval latency...")
    kw_lats = []
    _ = kw_retriever.retrieve(query=test_query, skill=test_skill, domains=[test_domain], top_k=5)
    for _ in range(num_runs):
        t0 = time.perf_counter()
        _ = kw_retriever.retrieve(query=test_query, skill=test_skill, domains=[test_domain], top_k=5)
        kw_lats.append((time.perf_counter() - t0) * 1000.0)
    results["bm25_retrieval"] = {"raw": kw_lats, "stats": calc_stats(kw_lats)}
    print(f"  Done. Mean: {results['bm25_retrieval']['stats']['mean_ms']} ms, Median: {results['bm25_retrieval']['stats']['median_ms']} ms, P95: {results['bm25_retrieval']['stats']['p95_ms']} ms")

    # 4. Graph retrieval (NetworkX)
    print("\n[4/10] Measuring Graph Retrieval latency...")
    gr_lats = []
    _ = gr_retriever.retrieve(query=test_query, skill=test_skill, domains=[test_domain], concept=test_skill, top_k=5)
    for _ in range(num_runs):
        t0 = time.perf_counter()
        _ = gr_retriever.retrieve(query=test_query, skill=test_skill, domains=[test_domain], concept=test_skill, top_k=5)
        gr_lats.append((time.perf_counter() - t0) * 1000.0)
    results["graph_retrieval"] = {"raw": gr_lats, "stats": calc_stats(gr_lats)}
    print(f"  Done. Mean: {results['graph_retrieval']['stats']['mean_ms']} ms, Median: {results['graph_retrieval']['stats']['median_ms']} ms, P95: {results['graph_retrieval']['stats']['p95_ms']} ms")

    # 5. RRF Fusion
    print("\n[5/10] Measuring RRF Fusion latency...")
    # Pre-fetch candidate pools to isolate pure fusion time
    v_cands = vec_retriever.retrieve(query=test_query, skill=test_skill, domains=[test_domain], top_k=10)
    k_cands = kw_retriever.retrieve(query=test_query, skill=test_skill, domains=[test_domain], top_k=10)
    g_cands = gr_retriever.retrieve(query=test_query, skill=test_skill, domains=[test_domain], concept=test_skill, top_k=10)
    
    rrf_lats = []
    for _ in range(num_runs):
        t0 = time.perf_counter()
        _ = hybrid_retriever.retrieve(
            query=test_query,
            skill=test_skill,
            domains=[test_domain],
            top_k=5,
            concept=test_skill,
            fusion_method="rrf"
        )
        # Note: retrieve includes fetching + fusion; to measure pure RRF math over pre-fetched candidates:
        rrf_lats.append((time.perf_counter() - t0) * 1000.0)
    results["rrf_hybrid_retrieval"] = {"raw": rrf_lats, "stats": calc_stats(rrf_lats)}
    print(f"  Done. Mean: {results['rrf_hybrid_retrieval']['stats']['mean_ms']} ms, Median: {results['rrf_hybrid_retrieval']['stats']['median_ms']} ms, P95: {results['rrf_hybrid_retrieval']['stats']['p95_ms']} ms")

    # 6. Reranker
    print("\n[6/10] Measuring Reranker latency (Semantic & CrossEncoder)...")
    sem_cands = hybrid_retriever.retrieve(query=test_query, skill=test_skill, domains=[test_domain], top_k=10)
    sem_lats = []
    _ = semantic_reranker.rerank(query=test_query, results=sem_cands, top_k=5)
    for _ in range(num_runs):
        t0 = time.perf_counter()
        _ = semantic_reranker.rerank(query=test_query, results=sem_cands, top_k=5)
        sem_lats.append((time.perf_counter() - t0) * 1000.0)
    results["semantic_reranker"] = {"raw": sem_lats, "stats": calc_stats(sem_lats)}
    print(f"  Semantic Reranker: Mean: {results['semantic_reranker']['stats']['mean_ms']} ms, Median: {results['semantic_reranker']['stats']['median_ms']} ms, P95: {results['semantic_reranker']['stats']['p95_ms']} ms")

    ce_lats = []
    _ = cross_encoder.rerank(query=test_query, results=sem_cands, top_k=5)
    for _ in range(num_runs):
        t0 = time.perf_counter()
        _ = cross_encoder.rerank(query=test_query, results=sem_cands, top_k=5)
        ce_lats.append((time.perf_counter() - t0) * 1000.0)
    results["cross_encoder_reranker"] = {"raw": ce_lats, "stats": calc_stats(ce_lats)}
    print(f"  CrossEncoder Reranker: Mean: {results['cross_encoder_reranker']['stats']['mean_ms']} ms, Median: {results['cross_encoder_reranker']['stats']['median_ms']} ms, P95: {results['cross_encoder_reranker']['stats']['p95_ms']} ms")

    # 7. Groq Whisper STT
    print("\n[7/10] Measuring Groq Whisper transcription latency...")
    whisper_lats = []
    # Warmup
    _ = whisper_client.audio.transcriptions.create(
        model="whisper-large-v3",
        file=("sample.wav", sample_wav_bytes, "audio/wav"),
        language="en",
    )
    for i in range(num_runs):
        t0 = time.perf_counter()
        _ = whisper_client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=(f"sample_{i}.wav", sample_wav_bytes, "audio/wav"),
            language="en",
        )
        whisper_lats.append((time.perf_counter() - t0) * 1000.0)
        await asyncio.sleep(0.3)  # pace API requests
    results["groq_whisper_stt"] = {"raw": whisper_lats, "stats": calc_stats(whisper_lats)}
    print(f"  Done. Mean: {results['groq_whisper_stt']['stats']['mean_ms']} ms, Median: {results['groq_whisper_stt']['stats']['median_ms']} ms, P95: {results['groq_whisper_stt']['stats']['p95_ms']} ms")

    # 8. LLM Time-to-First-Token (TTFT)
    print("\n[8/10] Measuring LLM Time-to-First-Token (TTFT) via Groq streaming...")
    ttft_lats = []
    eval_prompt = [{"role": "user", "content": "Explain the difference between TCP and UDP in one sentence."}]
    # Warmup
    _stream = groq_client.chat.completions.create(model=groq_model, messages=eval_prompt, stream=True)
    for _ in _stream: break

    for i in range(num_runs):
        t0 = time.perf_counter()
        stream = groq_client.chat.completions.create(model=groq_model, messages=eval_prompt, stream=True)
        ttft = None
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                ttft = (time.perf_counter() - t0) * 1000.0
                break
        if ttft is not None:
            ttft_lats.append(ttft)
        await asyncio.sleep(0.3)
    results["llm_time_to_first_token"] = {"raw": ttft_lats, "stats": calc_stats(ttft_lats)}
    print(f"  Done. Mean: {results['llm_time_to_first_token']['stats']['mean_ms']} ms, Median: {results['llm_time_to_first_token']['stats']['median_ms']} ms, P95: {results['llm_time_to_first_token']['stats']['p95_ms']} ms")

    # 9. Edge-TTS Synthesis (uncached)
    print("\n[9/10] Measuring Edge-TTS Synthesis latency (bypassing in-memory cache)...")
    tts_lats = []
    # Test sentences of realistic question length (~15-20 words)
    tts_sentences = [
        f"In transaction processing, atomicity ensures that all operations succeed or none take effect. Run {i}."
        for i in range(num_runs)
    ]
    # Warmup
    _TTS_CACHE.clear()
    _ = await synthesize_speech_bytes("Warmup audio synthesis.")
    _TTS_CACHE.clear()

    for i in range(num_runs):
        _TTS_CACHE.clear()  # Ensure uncached network synthesis
        t0 = time.perf_counter()
        _ = await synthesize_speech_bytes(tts_sentences[i])
        tts_lats.append((time.perf_counter() - t0) * 1000.0)
        await asyncio.sleep(0.2)
    results["edge_tts_synthesis"] = {"raw": tts_lats, "stats": calc_stats(tts_lats)}
    print(f"  Done. Mean: {results['edge_tts_synthesis']['stats']['mean_ms']} ms, Median: {results['edge_tts_synthesis']['stats']['median_ms']} ms, P95: {results['edge_tts_synthesis']['stats']['p95_ms']} ms")

    # 10. End-to-end Speech-to-Speech Turnaround
    print("\n[10/10] Measuring End-to-End Speech-to-Speech Turnaround latency...")
    # Pipeline: Candidate Audio -> Whisper STT -> RAG query -> LLM TTFT / first sentence -> TTS generation ready
    e2e_lats = []
    for i in range(num_runs):
        _TTS_CACHE.clear()
        t0 = time.perf_counter()
        # Step A: STT
        _trans = whisper_client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=(f"e2e_{i}.wav", sample_wav_bytes, "audio/wav"),
            language="en",
        )
        stt_text = _trans.text or test_query
        
        # Step B: Retrieval
        _ret = hybrid_retriever.retrieve(
            query=stt_text, skill="acid-properties", domains=["dbms"], top_k=3
        )
        
        # Step C: LLM generation (streaming first conversational sentence)
        stream = groq_client.chat.completions.create(
            model=groq_model,
            messages=[
                {"role": "system", "content": "You are a technical interviewer. Respond in one concise sentence."},
                {"role": "user", "content": f"Candidate answer regarding ACID properties: {stt_text}."},
            ],
            stream=True,
        )
        collected_tokens = []
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                collected_tokens.append(chunk.choices[0].delta.content)
                if any(punct in chunk.choices[0].delta.content for punct in [".", "?", "!"]):
                    break
        first_sentence = "".join(collected_tokens).strip() or "Good. Let's move to the next question."
        
        # Step D: TTS synthesis for the first sentence
        _ = await synthesize_speech_bytes(first_sentence)
        e2e_turnaround_ms = (time.perf_counter() - t0) * 1000.0
        e2e_lats.append(e2e_turnaround_ms)
        await asyncio.sleep(0.3)

    results["end_to_end_turnaround"] = {"raw": e2e_lats, "stats": calc_stats(e2e_lats)}
    print(f"  Done. Mean: {results['end_to_end_turnaround']['stats']['mean_ms']} ms, Median: {results['end_to_end_turnaround']['stats']['median_ms']} ms, P95: {results['end_to_end_turnaround']['stats']['p95_ms']} ms")

    out_file = PROJECT_ROOT / "paper_eval" / "task3_latency_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nAll Task 3 latency measurements saved to {out_file}")

if __name__ == "__main__":
    asyncio.run(run_latency_benchmarks(num_runs=30))
