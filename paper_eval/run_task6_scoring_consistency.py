"""
SmartInterview Paper Evidence - Task 6 Scoring Consistency Experiment
Evaluates 10 sample answers of mixed quality across 5 canonical CS questions.
Each answer is evaluated 5 times with:
  (i) LLM-only scoring (raw LLM technical correctness score)
  (ii) Full five-factor rubric (0.30*T + 0.20*C + 0.20*R + 0.15*S + 0.15*K)
Calculates mean and standard deviation per answer for both methods.
State model, temperature, and date.
"""

import os
import sys
import json
import time
import numpy as np
from datetime import date
from pathlib import Path
from typing import Dict, Any, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.services.question_service import (
    _init_rag,
    _init_groq,
    get_embedding_model,
    get_groq_client,
    get_groq_model_name,
)
from app.services.evaluation_service import (
    evaluate_answer,
    _llm_evaluate,
    _build_reference_text,
)
from app.rag.canonical_resolver import get_canonical_resolver

SAMPLE_DATASET = [
    # ── Question 1: DBMS (ACID Properties) ──
    {
        "q_id": "Q1_DBMS",
        "question": "What are the ACID properties in database transactions?",
        "domain": "dbms",
        "concept": "acid-properties",
        "difficulty": "medium",
        "bloom_level": "Understand",
        "answers": [
            {
                "ans_id": "Q1_A_Strong",
                "quality": "Strong",
                "text": (
                    "ACID stands for Atomicity, Consistency, Isolation, and Durability. "
                    "Atomicity guarantees all operations in a transaction succeed completely or roll back entirely (all-or-nothing). "
                    "Consistency ensures the database transitions between valid states, preserving all schema constraints and foreign keys. "
                    "Isolation ensures concurrently executing transactions do not interfere with one another, avoiding dirty or non-repeatable reads. "
                    "Durability guarantees that once committed, changes permanently survive system crashes or power failures via write-ahead logging."
                ),
            },
            {
                "ans_id": "Q1_B_Weak",
                "quality": "Weak",
                "text": (
                    "ACID makes transactions reliable. Atomicity means atomic operations, consistency keeps things consistent, "
                    "isolation means servers are isolated from each other, and durability means data stays on disk for a long time."
                ),
            },
        ],
    },
    # ── Question 2: Computer Networks (HTTP vs HTTPS) ──
    {
        "q_id": "Q2_CN",
        "question": "How is HTTP different from HTTPS?",
        "domain": "cn",
        "concept": "http-vs-https",
        "difficulty": "medium",
        "bloom_level": "Understand",
        "answers": [
            {
                "ans_id": "Q2_A_Strong",
                "quality": "Strong",
                "text": (
                    "HTTP transmits plaintext traffic over port 80 without encryption, leaving communication exposed to eavesdropping and MITM attacks. "
                    "HTTPS wraps HTTP traffic inside a TLS/SSL cryptographic tunnel over port 443. It authenticates the server via digital X.509 certificates "
                    "and performs an asymmetric handshake to establish symmetric session encryption, guaranteeing confidentiality, message integrity, and identity verification."
                ),
            },
            {
                "ans_id": "Q2_B_Weak",
                "quality": "Weak",
                "text": (
                    "HTTPS is just a secure version of HTTP. It has an extra 'S' and shows a green padlock in web browsers. "
                    "HTTP is older and less safe because hackers can read your passwords."
                ),
            },
        ],
    },
    # ── Question 3: Operating Systems (Process vs Thread) ──
    {
        "q_id": "Q3_OS",
        "question": "How is a process different from a thread?",
        "domain": "os",
        "concept": "process-vs-thread",
        "difficulty": "easy",
        "bloom_level": "Understand",
        "answers": [
            {
                "ans_id": "Q3_A_Strong",
                "quality": "Strong",
                "text": (
                    "A process is an executing program instance with its own isolated virtual memory address space, file descriptor table, and security context. "
                    "A thread is the smallest schedulable execution unit within a process. Multiple threads within the same process share the heap, global variables, "
                    "and code segments, but each thread possesses its own private stack and CPU registers. Context switching between threads incurs less overhead "
                    "because page tables do not need to be flushed."
                ),
            },
            {
                "ans_id": "Q3_B_Weak",
                "quality": "Weak",
                "text": (
                    "A process is a program you run like Microsoft Word. A thread is lightweight and does background tasks inside Java or Python. "
                    "Processes take more memory and take longer to start."
                ),
            },
        ],
    },
    # ── Question 4: Data Structures & Algorithms (Hash Table Collisions) ──
    {
        "q_id": "Q4_DSA",
        "question": "How does a hash table resolve collisions?",
        "domain": "dsa",
        "concept": "hash-table",
        "difficulty": "medium",
        "bloom_level": "Understand",
        "answers": [
            {
                "ans_id": "Q4_A_Strong",
                "quality": "Strong",
                "text": (
                    "Hash collisions occur when distinct keys hash to the same bucket index. The two primary resolution techniques are Separate Chaining "
                    "and Open Addressing. In separate chaining, each table index points to a linked list or self-balancing binary search tree holding colliding items. "
                    "In open addressing, all entries occupy the main table array directly; when a collision occurs, alternative vacant slots are located using probing sequences "
                    "such as linear probing, quadratic probing, or double hashing."
                ),
            },
            {
                "ans_id": "Q4_B_Weak",
                "quality": "Weak",
                "text": (
                    "Collisions happen when two keys get the same number from the hash function. You can fix this by chaining them into a list or finding the next open spot. "
                    "Resizing the hash table also helps prevent collisions."
                ),
            },
        ],
    },
    # ── Question 5: System Design (Distributed Caching) ──
    {
        "q_id": "Q5_SYS",
        "question": "Why do we use caching in distributed systems?",
        "domain": "system-design",
        "concept": "caching",
        "difficulty": "easy",
        "bloom_level": "Understand",
        "answers": [
            {
                "ans_id": "Q5_A_Strong",
                "quality": "Strong",
                "text": (
                    "In distributed systems, caching dramatically reduces read latencies and protects persistent storage databases from query saturation by exploiting temporal "
                    "and spatial locality. High-speed in-memory caches like Redis or Memcached serve hot data in sub-millisecond time. Standard caching patterns include "
                    "Cache-Aside, Write-Through, and Write-Back, coupled with TTLs and eviction policies like LRU or LFU to manage memory bounds and mitigate stale reads."
                ),
            },
            {
                "ans_id": "Q5_B_Weak",
                "quality": "Weak",
                "text": (
                    "Caching is used so websites load fast without hitting MySQL repeatedly. You put Redis in between the client and server to keep frequent data in RAM."
                ),
            },
        ],
    },
]

def run_scoring_consistency_experiment(repetitions: int = 5):
    print("=" * 75)
    print("SmartInterview — Task 6 Scoring Consistency Experiment")
    print(f"Date: {date.today().isoformat()} | Repetitions per answer: {repetitions}")
    print("=" * 75)

    _init_rag()
    _init_groq()
    embedding_model = get_embedding_model()
    groq_client = get_groq_client()
    groq_model = get_groq_model_name()
    resolver = get_canonical_resolver()

    print(f"Model: {groq_model}")
    print("Temperature: 0.3 (deterministic evaluation configuration)")

    experiment_results = []

    for q_entry in SAMPLE_DATASET:
        q_id = q_entry["q_id"]
        q_text = q_entry["question"]
        concept = q_entry["concept"]
        domain = q_entry["domain"]
        difficulty = q_entry["difficulty"]
        bloom_level = q_entry["bloom_level"]

        # Fetch canonical chunks for reference context
        canonical_chunks = resolver.get_chunks_for_concept(concept)
        rag_context = [
            {"chunk_id": c.chunk_id, "domain": c.domain, "concept": c.concept, "text": c.text}
            for c in canonical_chunks[:3]
        ]
        ref_text = _build_reference_text(rag_context)

        print(f"\nProcessing {q_id}: '{q_text}'")

        for ans_entry in q_entry["answers"]:
            ans_id = ans_entry["ans_id"]
            quality = ans_entry["quality"]
            ans_text = ans_entry["text"]

            print(f"  Evaluating {ans_id} ({quality})...")

            llm_only_scores = []
            five_factor_scores = []
            detailed_runs = []

            for rep in range(1, repetitions + 1):
                # 1. LLM-only evaluation
                llm_eval = _llm_evaluate(
                    question_text=q_text,
                    answer_text=ans_text,
                    difficulty=difficulty,
                    bloom_level_name=bloom_level,
                    reference_context=ref_text,
                    groq_client=groq_client,
                    groq_model=groq_model,
                )
                llm_score = llm_eval.get("technical_score", 0)
                llm_only_scores.append(llm_score)

                # 2. Full five-factor rubric
                full_eval = evaluate_answer(
                    question_text=q_text,
                    answer_text=ans_text,
                    difficulty=difficulty,
                    bloom_level_name=bloom_level,
                    rag_context=rag_context,
                    groq_client=groq_client,
                    groq_model=groq_model,
                    embedding_model=embedding_model,
                )
                full_score = full_eval.overall_score
                five_factor_scores.append(full_score)

                detailed_runs.append({
                    "run": rep,
                    "llm_technical": llm_score,
                    "full_overall": full_score,
                    "t": full_eval.technical_score,
                    "c": full_eval.completeness_score,
                    "r": full_eval.relevance_score,
                    "s": full_eval.semantic_similarity_score,
                    "k": full_eval.concept_coverage_score,
                })
                time.sleep(0.4)  # pace Groq API requests

            llm_mean = round(float(np.mean(llm_only_scores)), 2)
            llm_std = round(float(np.std(llm_only_scores)), 2)
            full_mean = round(float(np.mean(five_factor_scores)), 2)
            full_std = round(float(np.std(five_factor_scores)), 2)

            record = {
                "question_id": q_id,
                "answer_id": ans_id,
                "quality": quality,
                "question": q_text,
                "answer": ans_text,
                "llm_only": {
                    "scores": llm_only_scores,
                    "mean": llm_mean,
                    "std": llm_std,
                },
                "five_factor_rubric": {
                    "scores": five_factor_scores,
                    "mean": full_mean,
                    "std": full_std,
                },
                "runs": detailed_runs,
            }
            experiment_results.append(record)

            print(f"    -> LLM-only: Mean={llm_mean}, Std={llm_std} (Scores: {llm_only_scores})")
            print(f"    -> 5-Factor: Mean={full_mean}, Std={full_std} (Scores: {five_factor_scores})")

    out_file = PROJECT_ROOT / "paper_eval" / "task6_consistency_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "experiment_metadata": {
                    "title": "SmartInterview Task 6 Scoring Consistency Experiment",
                    "date": date.today().isoformat(),
                    "model": groq_model,
                    "temperature": 0.3,
                    "repetitions": repetitions,
                    "total_answers_evaluated": len(experiment_results),
                    "note": "Answers authored across 5 canonical CS questions representing strong and weak quality.",
                },
                "results": experiment_results,
            },
            f,
            indent=2,
        )

    print(f"\nSaved Task 6 consistency experiment results to {out_file}")

if __name__ == "__main__":
    run_scoring_consistency_experiment(repetitions=5)
