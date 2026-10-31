import subprocess
import json
import re
from pathlib import Path

# Mapping of phases to their test files
PHASE_MAPPING = {
    "Phase 1": [
        "tests/test_phase1_rag_baseline.py",
    ],
    "Phase 2-4": [
        "tests/test_phase2_graph_schema.py",
        "tests/test_phase3_graph_builder.py",
        "tests/test_phase3_graph_storage.py",
        "tests/test_phase4_canonical_chunk_resolution.py",
        "tests/test_phase4_graph_validator.py",
    ],
    "Phase 5": [
        "tests/test_phase5_bm25_retrieval.py",
        "tests/test_phase5_graph_storage.py",
    ],
    "Phase 6-7": [
        "tests/test_phase6_graph_retrieval.py",
        "tests/test_phase6_graph_retrieval_validation.py",
        "tests/test_phase7_hybrid_fusion_validation.py",
        "tests/test_phase7_keyword_retrieval.py",
    ],
    "Phase 8": [
        "tests/test_phase8_hybrid_retrieval.py",
        "tests/test_phase8_reranker_validation.py",
    ],
    "Phase 9-10": [
        "tests/test_phase9_pipeline_integration.py",
        "tests/test_phase9_reranker.py",
        "tests/test_phase10_adaptive_validation.py",
        "tests/test_phase10_bloom_adaptive.py",
    ],
    "Phase 11-13": [
        "tests/test_phase11_config_security_audit.py",
        "tests/test_phase11_evaluation.py",
        "tests/test_phase12_golden_dataset_audit.py",
        "tests/test_phase13_evaluation_metrics.py",
    ],
    "Phase 14-18": [
        "tests/test_phase14_frozen_baseline.py",
        "tests/test_phase15_individual_retrievers.py",
        "tests/test_phase16_hybrid_evaluation.py",
        "tests/test_phase17_question_generation.py",
        "tests/test_phase18_failure_modes_and_edge_cases.py",
    ],
}

EXPECTED_COUNTS = {
    "Phase 1": 25,
    "Phase 2-4": 69,
    "Phase 5": 34,
    "Phase 6-7": 48,
    "Phase 8": 36,
    "Phase 9-10": 39,
    "Phase 11-13": 48,
    "Phase 14-18": 56,
    "Total": 355
}

def count_tests_in_file(filepath):
    res = subprocess.run(["pytest", "--collect-only", "-q", filepath], capture_output=True, text=True)
    # Match lines like "test_... " or the summary "X tests collected"
    m = re.search(r"(\d+) tests? collected", res.stdout)
    if m:
        return int(m.group(1))
    return 0

def main():
    print("Verifying test distribution against expected counts...")
    total_found = 0
    results = {}
    for phase, files in PHASE_MAPPING.items():
        phase_total = 0
        file_counts = {}
        for f in files:
            cnt = count_tests_in_file(f)
            file_counts[f] = cnt
            phase_total += cnt
        expected = EXPECTED_COUNTS[phase]
        match = (phase_total == expected)
        results[phase] = {
            "files": file_counts,
            "total": phase_total,
            "expected": expected,
            "match": match
        }
        total_found += phase_total
        print(f"{phase}: {phase_total} tests (Expected: {expected}) -> {'MATCH' if match else 'MISMATCH'}")
        for f, cnt in file_counts.items():
            print(f"  - {f}: {cnt}")

    total_match = (total_found == EXPECTED_COUNTS['Total'])
    print(f"\nTotal: {total_found} tests (Expected: {EXPECTED_COUNTS['Total']}) -> {'MATCH' if total_match else 'MISMATCH'}")

if __name__ == "__main__":
    main()
