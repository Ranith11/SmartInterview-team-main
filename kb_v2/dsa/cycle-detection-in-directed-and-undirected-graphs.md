---
topic: Cycle Detection in directed and undirected graphs
domain: dsa
subtopics: []
sources:
  - title: "Wikipedia: Cycle (graph theory)"
    url: https://en.wikipedia.org/wiki/Cycle_(graph_theory)
    license: CC BY-SA 4.0
status: NEEDS_HUMAN
open_issues: 1
generator: openai/gpt-oss-120b
critic: openai/gpt-oss-20b
last_verified: 2026-10-02
human_reviewed: false
---
## Definition

A **cycle** in a graph is a non‑empty closed trail whose first and last vertices are the same and whose intermediate vertices are all distinct.  
* In a **directed graph** (digraph) a *directed cycle* is a closed directed trail `v₁ → v₂ → … → vₖ → v₁` with `v₁,…,vₖ` distinct.  
* In an **undirected graph** a *simple cycle* is a sequence `v₁ – v₂ – … – vₖ – v₁` (`k ≥ 3`) where each consecutive pair is joined by an edge and the vertices `v₁,…,vₖ` are distinct.  

A graph that contains no cycles is called **acyclic**; a directed acyclic graph is abbreviated **DAG**.

---

## How It Works

### 1. Depth‑First Search (DFS) – General Mechanism  

DFS explores vertices recursively, marking each vertex when first discovered (`visited`) and, for directed graphs, when it remains on the current recursion stack (`recStack`).  

*Directed graphs* – a back edge to a vertex that is still on the recursion stack signals a directed cycle.  

*Undirected graphs* – an edge to any already‑visited vertex **other than** the immediate parent indicates a cycle (the parent edge is ignored to avoid the trivial two‑vertex “cycle”).

#### Worked Example (undirected)

Graph: `V = {A,B,C,D}`, edges `{A‑B, B‑C, C‑A, C‑D}`  

```
DFS(A, parent = null)
  visited[A]=true
  for B:
    DFS(B, A) → visited[B]=true
      for C:
        DFS(C, B) → visited[C]=true
          neighbor A (already visited, A ≠ parent B) → cycle found (A‑B‑C‑A)
```

The algorithm stops as soon as the back edge `C‑A` is discovered.

### 2. Union‑Find (Disjoint Set Union) – Undirected Only  

Each vertex starts in its own set. For every edge `(u,v)` we `Find` the representatives `ru, rv`.  

* If `ru == rv` the edge connects two vertices already in the same component → a cycle exists.  
* Otherwise `Union(ru, rv)` merges the components.

#### Worked Example (undirected)

Edges processed in order: `(1,2)`, `(2,3)`, `(3,1)`  

* After first two edges the sets are `{1,2,3}`? actually after `(1,2)` → `{1,2}`, `{3}`; after `(2,3)` → `{1,2,3}`.  
* Processing `(3,1)`: `Find(3) = Find(1)`, so a cycle is reported.

Path compression and union‑by‑rank give amortised `α(V)` (inverse Ackermann) time per operation.

### 3. Kahn’s Topological Sort – Directed Graphs  

Kahn’s algorithm repeatedly removes vertices with indegree 0.  

1. Compute indegree of every vertex.  
2. Enqueue all indegree‑0 vertices.  
3. Dequeue a vertex, “process” it, and decrement indegree of its outgoing neighbours; newly zero‑indegree vertices are enqueued.  

If after the loop fewer than `|V|` vertices have been processed, the remaining vertices belong to at least one directed cycle.

#### Worked Example (directed)

Edges: `A→B`, `B→C`, `C→A`, `C→D`.  

Indegrees: `A:1, B:1, C:1, D:1`. No vertex has indegree 0, so the queue starts empty. Processed count = 0 < 4 → a cycle exists (`A→B→C→A`).

### 4. Tarjan’s Strongly Connected Components (SCC) – Directed Graphs  

Tarjan performs a single DFS, assigning each vertex an `index` and a `lowlink`. Vertices are kept on a stack until an SCC is completed (when `lowlink == index`).  

*Any SCC containing more than one vertex, or a single vertex with a self‑loop, constitutes a directed cycle.*

#### Worked Example (directed)

Graph: `1→2`, `2→3`, `3→1`, `3→4`.  

DFS order: 1 (index 0), 2 (1), 3 (2).  
`lowlink(3)` becomes 0 because of edge `3→1`. When backtracking, vertices 1‑2‑3 are popped as one SCC → cycle detected. Vertex 4 forms a trivial SCC without a cycle.

---

## Complexity

| Algorithm | Graph Type | Time | Space |
|-----------|------------|------|-------|
| DFS (recursive) | Directed / Undirected | **O(V + E)** | **O(V)** (visited + recursion stack) |
| Union‑Find (with path compression & union by rank) | Undirected | **O(E α(V))** | **O(V)** |
| Kahn’s Topological Sort | Directed | **O(V + E)** | **O(V + E)** (queue + indegree array) |
| Tarjan’s SCC | Directed | **O(V + E)** | **O(V)** (stack + index/lowlink arrays) |

All are linear‑time in the size of the input, which is optimal because any algorithm must inspect each vertex and edge at least once.

---

## Key Properties

* **Back edge = cycle** – In DFS, a back edge to an ancestor (directed) or to a visited non‑parent (undirected) is the definitive indicator of a cycle.  
* **Component merging** – Union‑Find reveals a cycle precisely when an edge tries to merge two vertices already in the same component.  
* **Indegree‑zero elimination** – Kahn’s algorithm removes all vertices that cannot belong to any directed cycle; leftovers must be cyclic.  
* **Strongly connected components** – Every SCC with ≥ 2 vertices (or a self‑loop) contains a directed cycle, but not every edge of a strongly connected digraph lies on a cycle.  
* **Self‑loops** – A self‑loop is a cycle of length 1; DFS must explicitly check for it because the parent‑check rule would otherwise ignore it.  
* **Parallel edges** – In a simple undirected graph parallel edges are disallowed; in multigraphs two parallel edges form a 2‑vertex cycle, which DFS would detect as a back edge to a visited vertex that is not the parent.

---

## Real‑World Use

| Domain | Example | Cycle‑Detection Role |
|--------|---------|----------------------|
| Operating Systems | Wait‑for graph for deadlock detection | A directed cycle means a set of processes waiting forever. |
| Build Systems / Package Managers | Dependency DAGs | Detecting a cycle prevents impossible build orders. |
| Electronic Design Automation | Netlist verification | Undirected cycles correspond to loops that must be identified for mesh generation. |
| Version Control (Git) | Commit ancestry graph | Ensuring the commit graph remains a DAG; a cycle would corrupt history. |
| Database Schemas | Foreign‑key reference graph | Cycles can violate normalization; detection flags design errors. |
| Network Routing (OSPF, BGP) | Route propagation graphs | Cycles cause routing loops; detection triggers mitigation. |

---

## Comparison

| Technique | Works On | Detects Any Cycle? | Finds Shortest Cycle? | Extra Information |
|-----------|----------|--------------------|-----------------------|-------------------|
| DFS (recursive) | Directed & Undirected | Yes | No (but a BFS variant can find the shortest undirected cycle) | Simple to implement; gives back‑edge list. |
| Union‑Find | Undirected only | Yes | No | Very fast for edge‑stream input; cannot handle direction. |
| Kahn’s Topological Sort | Directed only | Yes (by leftover vertices) | No | Also produces a topological order when acyclic. |
| Tarjan’s SCC | Directed only | Yes | No | Returns all SCCs, useful for further analysis (e.g., condensation graph). |

---

## Tradeoffs / When NOT to Use

* **DFS** – Recursion depth may exceed stack limits on massive graphs; iterative versions mitigate this.  
* **Union‑Find** – Inapplicable to directed graphs; also cannot identify *which* vertices form the cycle, only that one exists.  
* **Kahn’s algorithm** – Only tells whether a cycle exists; it does not locate the cycle nor work for undirected graphs.  
* **Tarjan’s SCC** – Slightly more complex to code; overkill if you only need a boolean answer for a small directed graph.  

Choose the simplest method that matches the graph type and the information you need (existence vs. actual cycle vertices).

---

## Interview Q&A

1. **Q:** How does DFS detect a cycle in a directed graph?  
   **A:** During DFS we maintain a recursion‑stack flag. When exploring an edge `v → w`, if `w` is already on the stack (`recStack[w] = true`) we have found a back edge, which proves a directed cycle.  
   **Follow‑up:** What modification is needed to also output the vertices of the cycle?  

2. **Q:** Why must the parent edge be ignored in undirected‑graph DFS?  
   **A:** The edge that led to the current vertex is always present and would otherwise be reported as a back edge, creating a false positive for a 2‑vertex “cycle”. Ignoring the parent ensures only genuine cycles are reported.  

3. **Q:** Explain how Union‑Find detects a cycle in an undirected graph.  
   **A:** Each vertex starts in its own set. For each edge `(u,v)`, we `Find` the set representatives. If they are equal, `u` and `v` are already connected, so adding the edge creates a cycle. Otherwise we `Union` the sets.  

4. **Q:** Can Kahn’s topological sort be used to find the *shortest* directed cycle?  
   **A:** No. Kahn’s algorithm only determines whether any directed cycle exists by checking if any vertices remain after all indegree‑0 vertices are removed. It does not locate cycles, let alone the shortest one.  

5. **Q:** What does Tarjan’s algorithm return that is useful beyond mere cycle detection?  
   **A:** It returns all strongly connected components. Any SCC with more than one vertex (or a self‑loop) contains a directed cycle, and the SCC decomposition is valuable for many other graph problems (e.g., condensation DAG).  

---

## Common Misconceptions

* **“A back edge in any DFS means a cycle.”**  
  In undirected graphs the edge to the parent is a back edge by definition but does **not** indicate a cycle; the parent must be excluded.

* **“Union‑Find works for directed graphs.”**  
  Union‑Find only merges undirected connectivity; direction information is lost, so it cannot detect directed cycles.

* **“Kahn’s algorithm finds the shortest directed cycle.”**  
  It only tells whether a cycle exists; finding the shortest directed cycle requires more specialized algorithms (e.g., BFS from each vertex).

* **“Strong connectivity implies every edge lies on a cycle.”**  
  Strong connectivity guarantees a directed path between any two vertices, but some edges may be bridges that are not part of any cycle.

* **“DFS automatically reports self‑loops as cycles.”**  
  A naïve DFS that only checks visited neighbours may miss a self‑loop unless the implementation explicitly tests `v → v`.

<!-- END -->
