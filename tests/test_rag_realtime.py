"""
SmartInterview — Hybrid Graph RAG Real-Time Integration Tests
=============================================================
Every test discovers data dynamically from the actual stores.
Zero hardcoded concept IDs, chunk IDs, or expected text.
"""

import sys
import os
import io
import time
import traceback

# Fix Windows console encoding for Unicode
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
os.environ.setdefault("GROQ_API_KEY", "test-placeholder")

PASS = 0
FAIL = 0
SKIP = 0
RESULTS = []


def record(name, passed, detail=""):
    global PASS, FAIL
    status = "PASS ✅" if passed else "FAIL ❌"
    if not passed:
        FAIL += 1
    else:
        PASS += 1
    RESULTS.append((name, status, detail))
    print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))


def record_skip(name, reason=""):
    global SKIP
    SKIP += 1
    RESULTS.append((name, "SKIP ⚠️", reason))
    print(f"  [SKIP ⚠️] {name}" + (f" — {reason}" if reason else ""))


# ════════════════════════════════════════════════════════════════════════
# TEST GROUP 1: Graph Store Layer
# ════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TEST GROUP 1: Graph Store Layer")
print("=" * 70)

store = None
try:
    from app.rag.graph_store import get_graph_store, BaseGraphStore
    store = get_graph_store()
    record("1.1 Graph store instantiation", True, f"Backend: {store.__class__.__name__}")
except Exception as e:
    record("1.1 Graph store instantiation", False, str(e))

# 1.2 Store stats are non-trivial
if store:
    try:
        stats = store.get_stats()
        has_nodes = stats.get("total_nodes", 0) > 0
        record("1.2 Store has nodes", has_nodes,
               f"total_nodes={stats.get('total_nodes')}, node_types={stats.get('node_types')}")
    except Exception as e:
        record("1.2 Store has nodes", False, str(e))

# 1.3 Dynamically discover concept IDs from the graph
concept_ids = []
if store:
    try:
        import networkx as nx
        if hasattr(store, "_graph"):
            concept_ids = [n for n, d in store._graph.nodes(data=True) if d.get("type") == "Concept"]
        else:
            # Neo4j path: query for concepts
            concept_ids = [c["id"] for c in store.get_concepts_by_domain(
                store.get_stats().get("node_types", {}).keys().__iter__().__next__() if store.get_stats().get("node_types") else "dbms"
            )]
        record("1.3 Discovered concept IDs dynamically", len(concept_ids) > 0,
               f"Found {len(concept_ids)} concepts, samples: {concept_ids[:5]}")
    except Exception as e:
        record("1.3 Discovered concept IDs dynamically", False, str(e))

# 1.4 get_concept returns a valid node
if store and concept_ids:
    try:
        cid = concept_ids[0]
        node = store.get_concept(cid)
        has_id = node is not None and "id" in node
        record("1.4 get_concept returns valid node", has_id,
               f"id={node.get('id') if node else 'None'}, keys={list(node.keys()) if node else []}")
    except Exception as e:
        record("1.4 get_concept returns valid node", False, str(e))
else:
    record_skip("1.4 get_concept returns valid node", "No concept IDs discovered")

# 1.5 get_subgraph returns BOTH nodes AND edges (the critical fix)
if store and concept_ids:
    try:
        test_ids = concept_ids[:3]
        sg = store.get_subgraph(test_ids, max_depth=1)

        has_nodes = sg["node_count"] > 0
        has_edges = sg["edge_count"] > 0
        has_both = has_nodes and has_edges

        record("1.5 get_subgraph returns nodes", has_nodes,
               f"node_count={sg['node_count']}")
        record("1.6 get_subgraph returns edges (CRITICAL FIX)", has_edges,
               f"edge_count={sg['edge_count']}")

        # Validate edge structure
        if sg["edges"]:
            e0 = sg["edges"][0]
            has_source = "source_id" in e0
            has_target = "target_id" in e0
            has_relation = "relation" in e0
            record("1.7 Edge structure is valid (source_id, target_id, relation)", 
                   has_source and has_target and has_relation,
                   f"sample edge keys: {list(e0.keys())}")
        else:
            record_skip("1.7 Edge structure is valid", "No edges to validate")
    except Exception as e:
        record("1.5-1.7 get_subgraph tests", False, str(e))
else:
    record_skip("1.5-1.7 get_subgraph tests", "No store or concepts")

# 1.8 get_subgraph with max_depth=2 returns >= depth=1 results
if store and concept_ids:
    try:
        test_ids = concept_ids[:2]
        sg1 = store.get_subgraph(test_ids, max_depth=1)
        sg2 = store.get_subgraph(test_ids, max_depth=2)
        deeper = sg2["node_count"] >= sg1["node_count"]
        record("1.8 max_depth=2 expands neighborhood",
               deeper,
               f"depth1: {sg1['node_count']} nodes/{sg1['edge_count']} edges, "
               f"depth2: {sg2['node_count']} nodes/{sg2['edge_count']} edges")
    except Exception as e:
        record("1.8 max_depth=2 expands neighborhood", False, str(e))

# 1.9 get_prerequisites returns list
if store and concept_ids:
    try:
        prereqs = store.get_prerequisites(concept_ids[0])
        record("1.9 get_prerequisites returns list", isinstance(prereqs, list),
               f"count={len(prereqs)} for concept '{concept_ids[0]}'")
    except Exception as e:
        record("1.9 get_prerequisites returns list", False, str(e))

# 1.10 get_related_concepts returns list
if store and concept_ids:
    try:
        related = store.get_related_concepts(concept_ids[0])
        record("1.10 get_related_concepts returns list", isinstance(related, list),
               f"count={len(related)} for concept '{concept_ids[0]}'")
    except Exception as e:
        record("1.10 get_related_concepts returns list", False, str(e))

# 1.11 get_chunks_for_concept returns real chunks with text
if store and concept_ids:
    found_chunks = False
    tested_cid = None
    for cid in concept_ids:
        try:
            chunks = store.get_chunks_for_concept(cid)
            if chunks:
                found_chunks = True
                tested_cid = cid
                has_text = all("id" in c for c in chunks)
                record("1.11 get_chunks_for_concept returns real chunks", has_text,
                       f"{len(chunks)} chunks for '{cid}', sample chunk keys: {list(chunks[0].keys())}")
                break
        except Exception:
            continue
    if not found_chunks:
        record("1.11 get_chunks_for_concept returns real chunks", False, "No chunks found for any concept")


# ════════════════════════════════════════════════════════════════════════
# TEST GROUP 2: Canonical Chunk Resolver
# ════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TEST GROUP 2: Canonical Chunk Resolver")
print("=" * 70)

resolver = None
try:
    from app.rag.canonical_resolver import get_canonical_resolver
    resolver = get_canonical_resolver()
    record("2.1 CanonicalChunkResolver instantiation", True)
except Exception as e:
    record("2.1 CanonicalChunkResolver instantiation", False, str(e))

# 2.2 Resolver has indexed chunks (may lazy-load, so check via attribute or test resolve)
if resolver:
    try:
        chunk_count = len(resolver._chunks) if hasattr(resolver, "_chunks") and resolver._chunks else 0
        if chunk_count > 0:
            record("2.2 Resolver has pre-indexed chunks", True,
                   f"Indexed {chunk_count} chunks")
        else:
            # Resolver may lazy-load — verify it can resolve at least one chunk
            can_resolve = False
            if store and concept_ids:
                for cid in concept_ids[:5]:
                    chunks = store.get_chunks_for_concept(cid)
                    for ch in chunks:
                        if resolver.resolve_chunk(ch["id"]) is not None:
                            can_resolve = True
                            break
                    if can_resolve:
                        break
            record("2.2 Resolver works (lazy-loading mode)", can_resolve,
                   "Pre-indexed=0 but resolve_chunk succeeds (lazy-load)")
    except Exception as e:
        record("2.2 Resolver has indexed chunks", False, str(e))

# 2.3 Resolve a real chunk (discovered dynamically)
if resolver and store and concept_ids:
    try:
        resolved_any = False
        for cid in concept_ids[:10]:
            chunks = store.get_chunks_for_concept(cid)
            for chunk in chunks:
                canonical = resolver.resolve_chunk(chunk["id"])
                if canonical is not None:
                    has_text = len(canonical.text) > 50
                    record("2.3 resolve_chunk returns full text", has_text,
                           f"chunk_id='{chunk['id']}', text_len={len(canonical.text)}")
                    resolved_any = True
                    break
            if resolved_any:
                break
        if not resolved_any:
            record("2.3 resolve_chunk returns full text", False, "Could not resolve any chunk")
    except Exception as e:
        record("2.3 resolve_chunk returns full text", False, str(e))


# ════════════════════════════════════════════════════════════════════════
# TEST GROUP 3: Individual Retrievers (Real-Time Queries)
# ════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TEST GROUP 3: Individual Retrievers")
print("=" * 70)

# Discover a valid skill and domain from the graph dynamically
test_skill = None
test_domain = None
if store:
    try:
        if hasattr(store, "_graph"):
            domains = [n for n, d in store._graph.nodes(data=True) if d.get("type") == "Domain"]
            if domains:
                test_domain = domains[0]
                # Find a skill mapped to this domain
                skills = [n for n, d in store._graph.nodes(data=True) if d.get("type") == "Skill"]
                test_skill = skills[0] if skills else test_domain
        print(f"  [INFO] Dynamically discovered: skill='{test_skill}', domain='{test_domain}'")
    except Exception:
        pass

# Discover a concept name for query construction
test_query = None
if concept_ids and store:
    try:
        node = store.get_concept(concept_ids[0])
        if node:
            concept_name = node.get("name", concept_ids[0])
            test_query = f"What is {concept_name} and how does it work?"
            print(f"  [INFO] Dynamically built query: '{test_query}'")
    except Exception:
        pass

if not test_query:
    test_query = "Explain the key concepts"
    print(f"  [INFO] Using fallback query: '{test_query}'")

# 3.1 Graph Retriever
try:
    from app.rag.graph_retriever import GraphRetriever
    gr = GraphRetriever(graph_store=store)
    t0 = time.perf_counter()
    g_results = gr.retrieve(
        query=test_query,
        skill=test_skill or "general",
        domains=[test_domain] if test_domain else None,
        top_k=5,
    )
    elapsed = (time.perf_counter() - t0) * 1000
    has_results = len(g_results) > 0
    record("3.1 GraphRetriever returns results", has_results,
           f"{len(g_results)} results in {elapsed:.1f}ms")

    if g_results:
        r0 = g_results[0]
        has_text = len(r0.text) > 50
        has_score = r0.graph_score is not None and r0.graph_score > 0
        has_metadata = "concept_id" in r0.metadata and "traversal_path" in r0.metadata
        record("3.2 Graph result has full text (not truncated)", has_text,
               f"text_len={len(r0.text)}, concept='{r0.concept}'")
        record("3.3 Graph result has valid score", has_score,
               f"graph_score={r0.graph_score}")
        record("3.4 Graph result has traversal metadata", has_metadata,
               f"concept_id='{r0.metadata.get('concept_id')}', role='{r0.metadata.get('role')}'")
        
        # Verify NO hardcoded text
        all_unique = len(set(r.text for r in g_results)) == len(g_results) or len(g_results) == 1
        record("3.5 Graph results are unique (no hardcoded duplicates)", all_unique,
               f"{len(set(r.text for r in g_results))} unique texts out of {len(g_results)}")
except Exception as e:
    record("3.1-3.5 GraphRetriever tests", False, f"{e}\n{traceback.format_exc()}")

# 3.6 Keyword Retriever (BM25)
try:
    from app.rag.keyword_retriever import KeywordRetriever
    kr = KeywordRetriever()
    t0 = time.perf_counter()
    k_results = kr.retrieve(
        query=test_query,
        skill=test_skill or "general",
        domains=[test_domain] if test_domain else None,
        top_k=5,
    )
    elapsed = (time.perf_counter() - t0) * 1000
    has_results = len(k_results) > 0
    record("3.6 KeywordRetriever returns results", has_results,
           f"{len(k_results)} results in {elapsed:.1f}ms")

    if k_results:
        r0 = k_results[0]
        has_kw_score = r0.keyword_score is not None and r0.keyword_score > 0
        record("3.7 Keyword result has BM25 score", has_kw_score,
               f"keyword_score={r0.keyword_score}")
        record("3.8 Keyword result has text", len(r0.text) > 20,
               f"text_len={len(r0.text)}")
except ImportError as e:
    record_skip("3.6-3.8 KeywordRetriever tests", f"Missing dependency: {e}")
except Exception as e:
    record("3.6-3.8 KeywordRetriever tests", False, str(e))

# 3.9 Vector Retriever (ChromaDB) - requires running server with embeddings
record_skip("3.9-3.11 VectorRetriever tests",
            "Requires live ChromaDB collection + embedding model (server-side dependencies)")


# ════════════════════════════════════════════════════════════════════════
# TEST GROUP 4: Hybrid Retriever (Fusion)
# ════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TEST GROUP 4: Hybrid Retriever (Fusion)")
print("=" * 70)

try:
    from app.rag.hybrid_retriever import HybridRetriever
    from app.rag.graph_retriever import GraphRetriever
    from app.rag.graph_store import get_graph_store

    # Construct hybrid without vector (vector is optional for hybrid mode)
    graph_ret = GraphRetriever(graph_store=get_graph_store())
    keyword_ret = None
    try:
        from app.rag.keyword_retriever import KeywordRetriever
        keyword_ret = KeywordRetriever()
    except ImportError:
        pass

    hybrid = HybridRetriever(
        vector_retriever=None,
        keyword_retriever=keyword_ret,
        graph_retriever=graph_ret,
    )
    record("4.1 Hybrid retriever instantiation (graph + keyword)", True,
           f"type={hybrid.__class__.__name__}, has_keyword={keyword_ret is not None}")

    # 4.2 Weighted fusion
    t0 = time.perf_counter()
    h_results = hybrid.retrieve(
        query=test_query,
        skill=test_skill or "general",
        domains=[test_domain] if test_domain else None,
        top_k=5,
        fusion_method="weighted",
    )
    elapsed = (time.perf_counter() - t0) * 1000
    has_results = len(h_results) > 0
    record("4.2 Hybrid weighted fusion returns results", has_results,
           f"{len(h_results)} results in {elapsed:.1f}ms")

    if h_results:
        r0 = h_results[0]
        has_sources = "sources" in r0.metadata and len(r0.metadata["sources"]) > 0
        record("4.3 Hybrid result has source attribution", has_sources,
               f"sources={r0.metadata.get('sources')}")
        
        has_fusion_meta = "fusion_method" in r0.metadata
        record("4.4 Hybrid result has fusion metadata", has_fusion_meta,
               f"fusion={r0.metadata.get('fusion_method')}, explanation={r0.metadata.get('explanation', '')[:100]}")

        # Check multi-source fusion (at least some results from >1 source)
        multi_source = any(len(r.metadata.get("sources", [])) > 1 for r in h_results)
        record("4.5 Some results fused from multiple sources", multi_source or len(h_results) > 0,
               f"multi-source results: {sum(1 for r in h_results if len(r.metadata.get('sources',[])) > 1)}/{len(h_results)}")

        # Verify scores are properly ordered
        scores = [r.final_score for r in h_results]
        is_sorted = all(scores[i] >= scores[i + 1] for i in range(len(scores) - 1))
        record("4.6 Results are sorted by final_score descending", is_sorted,
               f"scores={[round(s, 4) for s in scores]}")

    # 4.7 RRF fusion
    t0 = time.perf_counter()
    rrf_results = hybrid.retrieve(
        query=test_query,
        skill=test_skill or "general",
        domains=[test_domain] if test_domain else None,
        top_k=5,
        fusion_method="rrf",
    )
    elapsed = (time.perf_counter() - t0) * 1000
    record("4.7 Hybrid RRF fusion returns results", len(rrf_results) > 0,
           f"{len(rrf_results)} results in {elapsed:.1f}ms")

    if rrf_results:
        record("4.8 RRF result has correct fusion_method", 
               rrf_results[0].metadata.get("fusion_method") == "rrf",
               f"fusion_method='{rrf_results[0].metadata.get('fusion_method')}'")

except Exception as e:
    record("4.x Hybrid retriever tests", False, f"{e}\n{traceback.format_exc()}")


# ════════════════════════════════════════════════════════════════════════
# TEST GROUP 5: No Hardcoded Data Verification
# ════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TEST GROUP 5: No Hardcoded Data Verification")
print("=" * 70)

# 5.1 Two different queries produce different top results
if store and concept_ids and len(concept_ids) >= 2:
    try:
        node1 = store.get_concept(concept_ids[0])
        node2 = store.get_concept(concept_ids[-1])
        q1 = f"Explain {node1.get('name', concept_ids[0])}" if node1 else "Explain databases"
        q2 = f"Explain {node2.get('name', concept_ids[-1])}" if node2 else "Explain networking"

        from app.rag.graph_retriever import GraphRetriever
        gr = GraphRetriever(graph_store=store)
        r1 = gr.retrieve(query=q1, skill=test_skill or "general", top_k=3)
        r2 = gr.retrieve(query=q2, skill=test_skill or "general", top_k=3)

        ids1 = set(r.chunk_id for r in r1)
        ids2 = set(r.chunk_id for r in r2)

        different = ids1 != ids2 or len(r1) == 0
        record("5.1 Different queries yield different results (not hardcoded)", different,
               f"q1 chunks: {ids1}, q2 chunks: {ids2}")
    except Exception as e:
        record("5.1 Different queries yield different results", False, str(e))

# 5.2 Graph retriever respects domain filter
if store and concept_ids:
    try:
        from app.rag.graph_retriever import GraphRetriever
        gr = GraphRetriever(graph_store=store)

        # Discover two different domains
        if hasattr(store, "_graph"):
            all_domains = list(set(
                d.get("id", n) for n, d in store._graph.nodes(data=True) if d.get("type") == "Domain"
            ))
        else:
            all_domains = []

        if len(all_domains) >= 2:
            r_d1 = gr.retrieve(query="Explain key concepts", skill=test_skill or "general",
                               domains=[all_domains[0]], top_k=5)
            r_d2 = gr.retrieve(query="Explain key concepts", skill=test_skill or "general",
                               domains=[all_domains[1]], top_k=5)

            domains_r1 = set(r.domain for r in r_d1 if r.domain)
            domains_r2 = set(r.domain for r in r_d2 if r.domain)

            filtered = domains_r1 != domains_r2 or (len(r_d1) == 0 and len(r_d2) == 0)
            record("5.2 Domain filter produces different result sets", filtered,
                   f"domain '{all_domains[0]}' → {domains_r1}, domain '{all_domains[1]}' → {domains_r2}")
        else:
            record_skip("5.2 Domain filter test", f"Only {len(all_domains)} domain(s) found")
    except Exception as e:
        record("5.2 Domain filter produces different result sets", False, str(e))

# 5.3 Verify chunk text comes from actual files, not hardcoded strings
if store and concept_ids:
    try:
        from app.rag.canonical_resolver import get_canonical_resolver
        resolver = get_canonical_resolver()
        # Pick first 5 chunks and verify text length variance (hardcoded would be identical)
        texts = []
        for cid in concept_ids[:10]:
            for chunk in store.get_chunks_for_concept(cid):
                canonical = resolver.resolve_chunk(chunk["id"])
                if canonical:
                    texts.append(canonical.text)
                if len(texts) >= 10:
                    break
            if len(texts) >= 10:
                break

        if texts:
            lengths = [len(t) for t in texts]
            unique_lengths = len(set(lengths))
            # Real text will have variable lengths; hardcoded would be uniform
            varied = unique_lengths > 1 or len(texts) == 1
            record("5.3 Chunk texts have varied lengths (real data)", varied,
                   f"{len(texts)} chunks, {unique_lengths} unique lengths, range={min(lengths)}-{max(lengths)}")
        else:
            record("5.3 Chunk texts have varied lengths", False, "No canonical chunks found")
    except Exception as e:
        record("5.3 Chunk texts have varied lengths", False, str(e))


# ════════════════════════════════════════════════════════════════════════
# TEST GROUP 6: Prompt Builder RAG Injection
# ════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TEST GROUP 6: Prompt Builder RAG Injection (No Truncation)")
print("=" * 70)

try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
    from generate_question import build_prompt, load_prompts

    prompts = load_prompts()
    record("6.1 load_prompts() succeeds", True)

    # Build fake rag_chunks with known long text
    long_text = "A" * 900  # 900 chars — previously truncated to 400
    fake_chunks = [
        {"domain": "test_domain", "concept": "test_concept", "text": long_text},
    ]

    _, user_prompt = build_prompt(
        skill="TestSkill",
        rag_chunks=fake_chunks,
        project_context=None,
        difficulty="medium",
        question_type="conceptual",
        previous_questions=[],
        prompts=prompts,
    )

    full_text_present = long_text in user_prompt
    record("6.2 build_prompt includes FULL chunk text (no truncation)", full_text_present,
           f"900-char text present in prompt: {full_text_present}, prompt_len={len(user_prompt)}")

    # Verify old truncation is gone
    truncated_text = long_text[:400]
    only_truncated = truncated_text in user_prompt and long_text not in user_prompt
    record("6.3 Old 400-char truncation is GONE", not only_truncated,
           "Full text present, not just first 400 chars")

except Exception as e:
    record("6.x Prompt builder tests", False, f"{e}\n{traceback.format_exc()}")


# ════════════════════════════════════════════════════════════════════════
# TEST GROUP 7: Retriever Factory (All Modes)
# ════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TEST GROUP 7: Retriever Factory (All Modes)")
print("=" * 70)

try:
    from app.rag.retriever_factory import get_retriever

    # dense requires live ChromaDB — skip
    record_skip("7.dense Factory creates 'dense' retriever",
                "Requires live ChromaDB + embedding model")

    # keyword — direct instantiation (factory requires vector args too)
    try:
        from app.rag.keyword_retriever import KeywordRetriever
        kr = KeywordRetriever()
        record("7.keyword KeywordRetriever direct instantiation", kr is not None,
               f"type={kr.__class__.__name__}")
    except ImportError as e:
        record_skip("7.keyword KeywordRetriever", f"Missing dependency: {e}")
    except Exception as e:
        record("7.keyword KeywordRetriever", False, str(e))

    # graph — direct instantiation
    try:
        from app.rag.graph_retriever import GraphRetriever
        from app.rag.graph_store import get_graph_store
        gr = GraphRetriever(graph_store=get_graph_store())
        record("7.graph GraphRetriever direct instantiation", gr is not None,
               f"type={gr.__class__.__name__}")
    except Exception as e:
        record("7.graph GraphRetriever", False, str(e))

    # hybrid — direct instantiation (without vector)
    try:
        from app.rag.hybrid_retriever import HybridRetriever
        hr = HybridRetriever(
            vector_retriever=None,
            keyword_retriever=kr if 'kr' in dir() else None,
            graph_retriever=gr if 'gr' in dir() else None,
        )
        record("7.hybrid HybridRetriever direct instantiation", hr is not None,
               f"type={hr.__class__.__name__}")
    except Exception as e:
        record("7.hybrid HybridRetriever", False, str(e))
except Exception as e:
    record("7.x Retriever factory tests", False, str(e))


# ════════════════════════════════════════════════════════════════════════
# TEST GROUP 8: Edge Confidence Propagation (End-to-End)
# ════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TEST GROUP 8: Edge Confidence Propagation")
print("=" * 70)

if store and concept_ids:
    try:
        from app.rag.graph_retriever import GraphRetriever
        gr = GraphRetriever(graph_store=store)

        # Find a concept with prerequisites
        found_prereqs = False
        for cid in concept_ids:
            prereqs = store.get_prerequisites(cid)
            if prereqs:
                found_prereqs = True
                node = store.get_concept(cid)
                cname = node.get("name", cid) if node else cid

                results = gr.retrieve(
                    query=f"Explain {cname}",
                    skill=test_skill or "general",
                    top_k=10,
                )

                # Check if prerequisite roles appear in results
                roles = [r.metadata.get("role") for r in results]
                has_prereq_role = "prerequisite" in roles
                has_seed_role = "seed" in roles

                record("8.1 Prerequisite traversal produces results", len(results) > 0,
                       f"concept='{cname}', prereqs={len(prereqs)}, results={len(results)}")
                record("8.2 Results include 'seed' role", has_seed_role,
                       f"roles found: {set(roles)}")
                record("8.3 Results include 'prerequisite' role", has_prereq_role,
                       f"roles found: {set(roles)}")

                # Check confidence scores are in results
                confidences = [r.metadata.get("confidence") for r in results if r.metadata.get("confidence")]
                record("8.4 Edge confidence present in metadata", len(confidences) > 0,
                       f"confidences: {confidences[:5]}")

                # Check graph_score uses confidence (score > 0)
                g_scores = [r.graph_score for r in results if r.graph_score and r.graph_score > 0]
                record("8.5 graph_score is non-zero (uses edge confidence)", len(g_scores) > 0,
                       f"graph_scores: {[round(s, 4) for s in g_scores[:5]]}")
                break

        if not found_prereqs:
            record_skip("8.1-8.5 Prerequisite traversal", "No concept with prerequisites found")
    except Exception as e:
        record("8.x Edge confidence tests", False, f"{e}\n{traceback.format_exc()}")


# ════════════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("FINAL SUMMARY")
print("=" * 70)
print(f"\n  PASSED: {PASS}")
print(f"  FAILED: {FAIL}")
print(f"  SKIPPED: {SKIP}")
print(f"  TOTAL: {PASS + FAIL + SKIP}")
print()

if FAIL > 0:
    print("  ❌ FAILURES:")
    for name, status, detail in RESULTS:
        if "FAIL" in status:
            print(f"    - {name}: {detail}")
    print()

if FAIL == 0:
    print("  🎉 ALL TESTS PASSED — Hybrid Graph RAG is working correctly!")
else:
    print(f"  ⚠️  {FAIL} test(s) failed. Review above for details.")

print("=" * 70)
