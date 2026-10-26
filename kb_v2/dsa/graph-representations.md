---
topic: Graph representations
domain: dsa
subtopics: ["adjacency matrix", "adjacency list", "edge list"]
sources:
  - title: "Wikipedia: Graph neural network"
    url: https://en.wikipedia.org/wiki/Graph_neural_network
    license: CC BY-SA 4.0
status: AUTO_VERIFIED
open_issues: 0
generator: openai/gpt-oss-120b
critic: openai/gpt-oss-20b
last_verified: 2026-10-02
human_reviewed: false
---
## Definition

**Adjacency matrix** – a square \(|V|\times|V|\) array \(A\) where \(A[i][j]=1\) (or the edge weight) iff the directed edge \((v_i,v_j)\) belongs to \(E\). For undirected graphs the matrix is symmetric.

**Adjacency list** – an array (or hash map) of \(|V|\) containers; the container for vertex \(v_i\) stores all neighbours \(v_j\) such that \((v_i,v_j)\in E\). Each entry may also hold a weight.

**Edge list** – a flat collection of edge records \((u,v,w)\) (weight optional). The list enumerates every edge exactly once; it contains no explicit per‑vertex neighbour information.

All three are loss‑less: any graph can be transformed from one representation to another without losing vertices or edges.

---

## How It Works

### Adjacency matrix  
1. Allocate a 2‑D array `A[n][n]` (`n = |V|`).  
2. Initialise every cell to 0 (or ∞ for weighted graphs).  
3. For each edge \((u,v)\) in \(E\):  
   * `A[u][v] = 1` (or the weight).  
   * If the graph is undirected, also set `A[v][u] = 1`.  

**Worked example** – Graph \(V=\{0,1,2\}\), \(E=\{(0,1),(1,2)\}\) (undirected).  

```
   0 1 2          after insertion:
0 [0 1 0]   →   [0 1 0]
1 [1 0 1]   →   [1 0 1]
2 [0 1 0]   →   [0 1 0]
```

### Adjacency list  
1. Create `Adj[0…n‑1]`, each entry an empty dynamic array (or linked list).  
2. For each edge \((u,v)\):  
   * Append `v` (and weight if any) to `Adj[u]`.  
   * If undirected, also append `u` to `Adj[v]`.  

**Worked example** – Same graph as above.

```
Adj[0] = [1]
Adj[1] = [0,2]
Adj[2] = [1]
```

Iterating neighbours of 1 visits `[0,2]` in \(O(\deg(1))\) time.

### Edge list  
1. Initialise an empty vector `Elist`.  
2. For each edge \((u,v,w)\) push a record `{src:u, dst:v, weight:w}` onto `Elist`.  
3. For undirected graphs store each edge once (e.g., with `u < v`).  

**Worked example**

```
Elist = [ (0,1), (1,2) ]
```

Kruskal’s MST algorithm sorts `Elist` by weight, then processes edges in order.

---

## Complexity

| Operation | Adjacency matrix | Adjacency list | Edge list |
|-----------|------------------|----------------|-----------|
| **Space** | \(\Theta(|V|^2)\) | \(\Theta(|V|+|E|)\) | \(\Theta(|E|)\) |
| Add vertex | \(\Theta(|V|^2)\) (re‑allocate) | \(O(1)\) amortised | \(O(1)\) |
| Add edge | \(O(1)\) | \(O(1)\) amortised | \(O(1)\) |
| Remove edge | \(O(1)\) | \(O(\deg(u))\) (search) | \(O(|E|)\) (scan) |
| Edge‑existence query | \(O(1)\) | \(O(\deg(u))\) | \(O(|E|)\) |
| Iterate neighbours of u | \(O(|V|)\) (scan row) | \(O(\deg(u))\) | – (must scan whole list) |
| Iterate all edges | \(O(|V|^2)\) | \(O(|E|)\) | \(O(|E|)\) |

Time‑space trade‑offs depend heavily on graph density.

---

## Key Properties

* **Density sensitivity** – matrices excel for dense graphs (\(|E|≈|V|^2\)); lists and edge lists are optimal for sparse graphs.  
* **Random access** – constant‑time edge existence in a matrix; list gives constant‑time insertion but linear‑time lookup in the degree.  
* **Cache locality** – matrix rows are contiguous, benefitting SIMD/GPU kernels; list/edge list involve pointer chasing.  
* **Mutability** – adding/removing vertices is cheap for list and edge list, expensive for matrix due to reallocation.  
* **Weighted support** – all three can store weights; matrix stores them directly, list stores per‑neighbour, edge list stores per‑record.  
* **Directed vs. undirected** – matrix stores asymmetric entries for directed graphs; list stores separate adjacency entries; edge list stores ordered pairs.

---

## Real‑World Use

| Scenario | Preferred representation | Reason |
|----------|--------------------------|--------|
| **Social‑network friend graph** (billions of users, avg degree ≈ 200) | Adjacency list (often CSR compressed) | Extremely sparse; neighbour iteration dominates. |
| **Road network for a city** (few thousand intersections, weighted edges) | Adjacency list with weights | Sparse, weighted, frequent Dijkstra/ A* queries. |
| **Small dense circuit simulation** (≤ 500 nodes) | Adjacency matrix | Memory acceptable; constant‑time edge checks simplify Boolean‑matrix algorithms. |
| **Kruskal’s Minimum Spanning Tree** | Edge list (sorted by weight) | Global sorting of edges required; adjacency not needed. |
| **All‑pairs shortest paths (Floyd‑Warshall)** | Adjacency matrix | Algorithm is a series of matrix multiplications; matrix form is natural. |

---

## Comparison

| Aspect | Matrix | List | Edge list |
|--------|--------|------|-----------|
| **Space** | \(O(|V|^2)\) | \(O(|V|+|E|)\) | \(O(|E|)\) |
| **Edge lookup** | \(O(1)\) | \(O(\deg)\) | \(O(|E|)\) |
| **Neighbour iteration** | \(O(|V|)\) | \(O(\deg)\) | – |
| **Best for** | Dense graphs, algorithms using matrix algebra | Sparse graphs, frequent neighbour traversal | Algorithms that process edges globally (sorting, filtering) |
| **Cache behaviour** | High locality | Moderate (depends on container) | Poor (linked structures) |
| **Ease of parallelisation** | Excellent (matrix ops) | Good with edge‑partitioning | Good for embarrassingly parallel edge scans |

---

## Tradeoffs / When NOT to Use

* **Do not use an adjacency matrix** for a web‑scale graph with millions of vertices and average degree < 10; the \(|V|^2\) memory blows up.  
* **Do not use an adjacency list** when you need constant‑time edge existence checks for a dense graph; the linear scan of a neighbour list becomes a bottleneck.  
* **Do not use an edge list** if the algorithm repeatedly queries “who are the neighbours of u?” – you would have to scan the whole list each time, leading to \(O(|E|)\) per query.  

Choosing the wrong representation can increase both runtime and memory by orders of magnitude.

---

## Interview Q&A

1. **Q:** *When would you prefer an adjacency matrix over an adjacency list?*  
   **A:** When the graph is dense (\(|E| = Θ(|V|^2)\)) or when the algorithm requires frequent \(O(1)\) edge‑existence checks (e.g., Floyd‑Warshall).  
   **Follow‑up:** *What is the memory impact for a graph with 10⁴ vertices?* – About 100 MB for a Boolean matrix (10⁴ × 10⁴ ≈ 10⁸ bits ≈ 12.5 MB; with 4‑byte ints it’s ≈ 400 MB).

2. **Q:** *How do you add a new vertex to an adjacency list representation?*  
   **A:** Append an empty container to the primary array (or insert a new key in a hash map). This is \(O(1)\) amortised.  
   **Follow‑up:** *What extra work is needed for a matrix?* – Reallocate a larger \( (n+1)×(n+1) \) array and copy existing data, costing \(Θ(n^2)\).

3. **Q:** *Explain how Kruskal’s algorithm benefits from an edge‑list representation.*  
   **A:** Kruskal first sorts all edges by weight; an edge list can be sorted in \(O(|E|\log|E|)\) time and then processed sequentially with a Union‑Find structure. No adjacency information is required.  
   **Follow‑up:** *Would an adjacency list be slower?* – Yes, because you’d need to extract all edges from the lists before sorting, adding extra \(O(|V|+|E|)\) overhead.

4. **Q:** *What is the time complexity of checking whether two vertices are adjacent in each representation?*  
   **A:** Matrix \(O(1)\); List \(O(\deg(u))\) (linear scan of u’s neighbour list); Edge list \(O(|E|)\) (scan whole list).  
   **Follow‑up:** *How can you improve the list case?* – Store each neighbour list in a hash set or balanced BST, giving expected \(O(1)\) or \(O(\log\deg)\) lookup at the cost of extra space.

5. **Q:** *Describe a scenario where converting from an adjacency list to an edge list is advantageous.*  
   **A:** When you need to run a global edge‑centric algorithm such as Borůvka’s MST or edge‑based parallel processing; the edge list provides a flat structure that can be partitioned across threads without contention.  
   **Follow‑up:** *What is the conversion cost?* – Linear in the number of edges, \(O(|E|)\), by iterating each adjacency list once.

---

## Common Misconceptions

* **“Adjacency list always uses less memory than matrix.”** – False for dense graphs; when \(|E|≈|V|^2\) the list’s overhead (pointers, container metadata) can exceed the matrix’s raw storage.  
* **“Edge list gives fast neighbour queries.”** – Incorrect; edge lists lack per‑vertex indexing, so neighbour queries are \(O(|E|)\). They are only fast for algorithms that treat edges as independent items.  
* **“You can’t store weights in an adjacency matrix.”** – Wrong; each cell can hold a numeric weight (or ∞ for no edge).  
* **“Adding a vertex to a matrix is cheap because you just add a row.”** – In practice you must allocate a new \( (n+1)×(n+1) \) array and copy all existing entries, which is \(Θ(n^2)\).  
* **“All three representations are interchangeable with zero overhead.”** – Conversions cost linear time in the size of the source representation and may temporarily double memory usage.

<!-- END -->
