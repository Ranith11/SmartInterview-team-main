---
topic: AVL Tree
domain: dsa
subtopics: ["rotations: LL", "RR", "LR", "RL", "balancing factor"]
sources:
  - title: "Wikipedia: AVL tree"
    url: https://en.wikipedia.org/wiki/AVL_tree
    license: CC BY-SA 4.0
status: AUTO_VERIFIED
open_issues: 0
generator: openai/gpt-oss-120b
critic: openai/gpt-oss-20b
last_verified: 2026-10-02
human_reviewed: false
---
## Definition  
An **AVL tree** is a self‑balancing binary search tree in which every node *v* stores a **balance factor**  

\[
\text{BF}(v)=\text{height}(v_{\text{right}})-\text{height}(v_{\text{left}})
\]

that must belong to the set \{-1, 0, +1\}.  
If any node’s balance factor leaves this range, the tree is rebalanced by one or more **rotations**. Because the height *h* of an AVL tree with *n* nodes satisfies  

\[
\log_{2}(n+1)\le h < \log_{\varphi}(n+2)+b\qquad(\varphi\approx1.618),
\]

all basic operations run in \(O(\log n)\) time.

---

## How It Works  

### Balancing Factor  
The balance factor is computed from the heights of the left and right sub‑trees.  
*Example*:  

```
        30
       /  \
      20   40
     / \
    10 25
```

Heights: left subtree of 30 = 2, right subtree = 1 → BF(30)=1‑2 = –1 (left‑heavy). All other nodes have BF ∈ {‑1,0,1}, so the tree is AVL‑valid.

### LL Rotation (single right rotation)  
**When it occurs**: a node *z* becomes left‑heavy (BF = –2) and its left child *y* is also left‑heavy (BF ≤ 0).  

**Mechanism** – rotate right around *z*:  

```
        z                               y
       / \        →                    / \
      y   C                           A   z
     / \                                 / \
    A   B                               B   C
```

**Worked example** – Insert 5 into the AVL tree below (keys in order):  

```
      30
     /  \
    20   40
   /
 10
```

After inserting 5 as left child of 10, BF(20) = –2, BF(10) = –1 → LL case at *z*=20, *y*=10. Performing the right rotation yields  

```
      30
     /  \
    10   40
   / \
  5  20
```

All balance factors are now within \{-1,0,1\}.

### RR Rotation (single left rotation)  
**When it occurs**: a node *z* is right‑heavy (BF = +2) and its right child *y* is also right‑heavy (BF ≥ 0).  

**Mechanism** – rotate left around *z*:  

```
    z                               y
   / \        →                    / \
  A   y                           z   C
     / \                         / \
    B   C                       A   B
```

**Worked example** – Starting from  

```
      10
        \
         20
           \
            30
```

Insertion of 30 makes BF(10)=+2, BF(20)=+1 → RR case at *z*=10, *y*=20. Left rotation gives  

```
      20
     /  \
    10  30
```

Tree is balanced.

### LR Rotation (left‑right double rotation)  
**When it occurs**: a node *z* is left‑heavy (BF = –2) but its left child *y* is right‑heavy (BF = +1).  

**Mechanism** – first rotate left around *y*, then right around *z*:  

```
   z               z               y
  / \   LR →     / \   →        /   \
 y   C          B   C           z     C
/ \                / \         / \
A   B              A   B       A   B
```

**Worked example** – Insert 25 into  

```
      30
     /  
    10
      \
       20
```

After insertion, BF(30)=–2, BF(10)=+1 → LR case.  

1. Left rotate on *y*=10 →  

```
      30
     /  
    20
   /
 10
```

2. Right rotate on *z*=30 →  

```
      20
     /  \
    10  30
```

All nodes now have BF ∈ {‑1,0,1}.

### RL Rotation (right‑left double rotation)  
**When it occurs**: a node *z* is right‑heavy (BF = +2) and its right child *y* is left‑heavy (BF = –1).  

**Mechanism** – first rotate right around *y*, then left around *z*:  

```
 z                z                y
/ \   RL →      / \   →         /   \
A   y          A   B           z     C
   / \            / \         / \
  B   C          B   C       A   B
```

**Worked example** – Insert 15 into  

```
      10
        \
         30
        /
       20
```

After insertion, BF(10)=+2, BF(30)=–1 → RL case.  

1. Right rotate on *y*=30 →  

```
      10
        \
         20
           \
            30
```

2. Left rotate on *z*=10 →  

```
      20
     /  \
    10  30
```

Tree is balanced.

---

## Complexity  
| Operation | Worst‑case Time | Extra Space |
|-----------|----------------|-------------|
| Search    | \(O(\log n)\)  | \(O(1)\) (recursion stack \(O(\log n)\)) |
| Insert    | \(O(\log n)\)  | \(O(1)\) (or \(O(\log n)\) stack) |
| Delete    | \(O(\log n)\)  | \(O(1)\) (or \(O(\log n)\) stack) |
| Single rotation (LL/RR) | \(O(1)\) | \(O(1)\) |
| Double rotation (LR/RL) | \(O(1)\) | \(O(1)\) |

The tree stores one extra signed integer (or two bits) per node for the balance factor, giving overall space \(O(n)\).

---

## Key Properties  
* **Strict height balance** – max height ≈ 1.44 · log₂ n, tighter than many balanced BSTs.  
* **Deterministic \(O(\log n)\) operations** – no amortization needed.  
* **At most one (single or double) rotation per insertion**; deletions may trigger up to \(O(\log n)\) rotations.  
* **In‑order traversal yields sorted keys** – same as any BST.  
* **Balance factor can be stored in two bits**, making the overhead minimal.

---

## Real‑World Use  
* **Database indexing** where read‑heavy workloads demand consistently fast lookups.  
* **Memory‑constrained embedded systems** because the extra per‑node storage is tiny.  
* **Compilers and interpreters** for symbol tables that require predictable query time.  
* **Geographic information systems** where range queries benefit from the tighter height bound.

---

## Comparison  
| Structure | Height bound | Rotations per insert | Rotations per delete | Typical use case |
|-----------|--------------|----------------------|----------------------|------------------|
| AVL       | ≤ 1.44 · log₂ n | ≤ 2 (single or double) | ≤ O(log n) | Read‑intensive, strict performance guarantees |
| Red‑Black | ≤ 2 · log₂ n   | ≤ 2 (single or double) | ≤ 2 (single)        | Write‑heavy workloads, simpler implementation |
| B‑Tree    | ≤ log₍m₎ n (m‑way) | N/A (node split) | N/A (node merge)    | Disk‑based storage, large blocks |

AVL trees give faster lookups than red‑black trees because they stay shorter, but they may require more rebalancing work on deletions.

---

## Tradeoffs / When NOT to Use  
* **Write‑heavy applications** – frequent inserts/deletes cause many rotations, hurting throughput.  
* **Very large datasets on disk** – AVL’s node‑centric structure leads to many pointer hops; B‑trees are preferred.  
* **Concurrent environments** – AVL rotations touch multiple pointers; lock‑free or lock‑based concurrent trees are more complex than lock‑free red‑black variants.  

If the workload is dominated by updates or the data resides on secondary storage, consider red‑black trees, B‑trees, or skip lists instead.

---

## Interview Q&A  

1. **Q:** *Why does an AVL tree guarantee \(O(\log n)\) search?*  
   **A:** Because the balance factor restriction forces the height *h* to satisfy \(h < \log_{\varphi}(n+2)+b\), which is Θ(log n). Search follows a root‑to‑leaf path of length ≤ h, so it is \(O(\log n)\).  
   **Follow‑up:** *What is the worst‑case height for 1 000 000 nodes?* – Approximately \(1.44·\log_2 10^6 ≈ 28\) levels.

2. **Q:** *Explain the LL rotation with a concrete example.*  
   **A:** (Provide the example from the “LL Rotation” subsection). After inserting 5, node 20 becomes unbalanced (BF = –2) with left child 10 also left‑heavy. A right rotation around 20 moves 10 up and 20 down, restoring balance.  
   **Follow‑up:** *What happens to the balance factors after the rotation?* – They become 0 for the new root of the rotated subtree and are recomputed for its children based on their new heights.

3. **Q:** *How many rotations can a single deletion cause?*  
   **A:** Deleting a node may require a rotation at each ancestor where the balance factor becomes ±2, so up to \(O(\log n)\) rotations in the worst case.  
   **Follow‑up:** *Why can a rotation after deletion sometimes leave the subtree’s height unchanged?* – When the sibling of the rebalanced node has BF = 0, the rotation restores balance without reducing the subtree height, stopping further retracing.

4. **Q:** *Compare AVL and red‑black trees in terms of lookup speed.*  
   **A:** AVL trees are more strictly balanced, giving a smaller height bound, so lookups traverse fewer nodes on average. Red‑black trees allow a height up to twice that of AVL, making lookups slightly slower but they need fewer rotations on updates.  
   **Follow‑up:** *Give a scenario where a red‑black tree would be preferred.* – In a write‑heavy workload where the cost of frequent rotations outweighs the marginally slower reads.

5. **Q:** *What information must be stored in each AVL node to support O(1) rebalancing?*  
   **A:** Either the height of the node or its balance factor (a signed integer in \{-1,0,1\}); two bits are sufficient.  
   **Follow‑up:** *How does storing only the balance factor affect height calculations?* – Height can be derived recursively when needed, but balance‑factor updates are cheaper because they depend only on the change in child heights.

---

## Common Misconceptions  

* **“AVL trees never need double rotations.”** – Incorrect; LR and RL cases arise when the child of an unbalanced node is heavy in the opposite direction.  
* **“Balance factor is height(left) – height(right).”** – The Wikipedia definition uses right minus left; both conventions work as long as the sign convention is consistent.  
* **“A single rotation always fixes the tree after deletion.”** – Deletion can propagate imbalance upward; multiple rotations may be required.  
* **“AVL trees are always faster than red‑black trees.”** – For read‑only workloads they are, but for heavy updates the extra rotations can make them slower.  
* **“Storing the balance factor requires a full integer per node.”** – Only two bits are needed because the factor is limited to \{-1,0,1\}.

<!-- END -->
