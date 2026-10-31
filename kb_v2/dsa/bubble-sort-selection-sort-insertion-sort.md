---
topic: Bubble Sort, Selection Sort, Insertion Sort
domain: dsa
subtopics: ["quadratic time sorting"]
sources:
  - title: "Wikipedia: Selection sort"
    url: https://en.wikipedia.org/wiki/Selection_sort
    license: CC BY-SA 4.0
status: AUTO_VERIFIED
open_issues: 0
generator: openai/gpt-oss-120b
critic: openai/gpt-oss-20b
last_verified: 2026-10-02
human_reviewed: false
---
## Definition  

**Quadratic‑time sorting** refers to the family of simple comparison‑based algorithms whose worst‑case running time grows proportionally to \(n^{2}\) (where \(n\) is the number of elements). The three classic members are **Bubble Sort**, **Selection Sort**, and **Insertion Sort**. All three are in‑place (use \(O(1)\) extra space) and are stable only when explicitly designed to be so. They are useful for teaching fundamentals and for very small inputs, but they become impractical once \(n\) exceeds a few dozen elements.

---

## How It Works  

### Bubble Sort  

1. **Passes** – Perform up to \(n-1\) passes over the array.  
2. **Adjacent compare‑swap** – In each pass, scan from index 0 to \(n-2-i\) (comparing \(A[j]\) and \(A[j+1]\)). If \(A[j] > A[j+1]\) swap them.  
3. **Early‑exit flag** – Keep a Boolean `swapped`. If a full pass makes no swap, the array is already sorted and the algorithm stops.  

**Worked example (array [5, 1, 4, 2, 8])**  

| Pass | Array after inner loop | Swapped? |
|------|------------------------|----------|
| 0 | **[1, 5, 4, 2, 8] → [1, 4, 5, 2, 8] → [1, 4, 2, 5, 8]** (8 stays) | Yes |
| 1 | **[1, 4, 2, 5, 8] → [1, 2, 4, 5, 8]** | Yes |
| 2 | No swaps (array already sorted) → stop | No |

Result: [1, 2, 4, 5, 8].

---

### Selection Sort  

1. **Outer index \(i\)** – Treat \(A[0…i-1]\) as the sorted prefix.  
2. **Find minimum** – Scan the unsorted suffix \(A[i…n-1]\) to locate the smallest element’s index `minIdx`.  
3. **Swap** – Exchange \(A[i]\) with \(A[minIdx]\) (if they differ).  
4. Increment \(i\) and repeat until \(i = n-1\).  

**Worked example (array [64, 25, 12, 22, 11])**  

| i | Scan (min) | Swap | Array after step |
|---|------------|------|------------------|
|0| min = 11 at index 4 | swap A[0]↔A[4] | **[11, 25, 12, 22, 64]** |
|1| min = 12 at index 2 | swap A[1]↔A[2] | **[11, 12, 25, 22, 64]** |
|2| min = 22 at index 3 | swap A[2]↔A[3] | **[11, 12, 22, 25, 64]** |
|3| min = 25 (already at 3) | no swap | **[11, 12, 22, 25, 64]** |

Result: [11, 12, 22, 25, 64].

---

### Insertion Sort  

1. **Iterate** \(i\) from 1 to \(n-1\); the subarray \(A[0…i-1]\) is kept sorted.  
2. **Key extraction** – Store `key = A[i]`.  
3. **Shift larger elements** – While \(j ≥ 0\) and \(A[j] > key\), move \(A[j]\) to \(A[j+1]\) and decrement \(j\).  
4. **Insert** – Place `key` at \(A[j+1]\).  

**Worked example (array [5, 2, 4, 6, 1, 3])**  

| i | key | Shifts | Array after insertion |
|---|-----|--------|-----------------------|
|1|2|5 → right → **[5, 5, 4, 6, 1, 3]**|**[2, 5, 4, 6, 1, 3]**|
|2|4|5 → right → **[2, 5, 5, 6, 1, 3]**|**[2, 4, 5, 6, 1, 3]**|
|3|6|no shift|**[2, 4, 5, 6, 1, 3]**|
|4|1|6,5,4,2 shift right → **[2, 4, 5, 6, 6, 3] → … → [2, 2, 4, 5, 6, 3]**|**[1, 2, 4, 5, 6, 3]**|
|5|3|6,5,4 shift → **[1, 2, 4, 5, 6, 6] → … → [1, 2, 4, 5, 5, 6]**|**[1, 2, 3, 4, 5, 6]**|

Result: [1, 2, 3, 4, 5, 6].

---

## Complexity  

| Algorithm | Comparisons (worst) | Swaps / Shifts (worst) | Time (Θ) | Space |
|-----------|--------------------|------------------------|----------|-------|
| Bubble Sort | \(\frac{n(n-1)}{2}\) | \(\frac{n(n-1)}{2}\) (swap each inversion) | \(\Theta(n^{2})\) | \(O(1)\) |
| Selection Sort | \(\frac{n(n-1)}{2}\) | at most \(n-1\) swaps | \(\Theta(n^{2})\) | \(O(1)\) |
| Insertion Sort | \(\Theta(n^{2})\) (average) – \(n-1\) best | \(\Theta(n^{2})\) shifts (worst) | \(\Theta(n^{2})\) | \(O(1)\) |

*Best case*: Bubble = \(Θ(n)\) with early‑exit; Insertion = \(Θ(n)\) when already sorted; Selection = \(Θ(n^{2})\) (still scans all).  

*Stability*: Bubble and Insertion are naturally stable; Selection is not unless modified with shifts.

---

## Key Properties  

* **In‑place** – All three use constant extra memory.  
* **Stability** – Bubble & Insertion preserve relative order of equal keys; Selection does not by default.  
* **Adaptivity** – Bubble (with flag) and Insertion run in linear time on nearly sorted data; Selection never adapts.  
* **Write‑efficiency** – Selection performs the fewest writes (≤ \(n-1\) swaps), making it attractive for flash/EEPROM where writes are costly.  
* **Cache behavior** – Bubble and Insertion exhibit good locality because they walk sequentially; Selection’s inner scan also accesses memory sequentially but repeats full passes, leading to more total memory traffic.

---

## Real‑World Use  

* **Educational tools** – Demonstrating basic sorting concepts and algorithmic analysis.  
* **Tiny embedded systems** – When \(n ≤ 20\) and deterministic memory usage outweighs speed.  
* **Write‑limited media** – Selection Sort for sorting data that must be written to EEPROM or flash a minimal number of times.  
* **Online insertion** – Insertion Sort shines when data arrives incrementally (e.g., maintaining a sorted list while reading a stream).  

---

## Comparison  

| Aspect | Bubble Sort | Selection Sort | Insertion Sort |
|--------|-------------|----------------|----------------|
| Comparisons | Always \(≈\frac{n^{2}}{2}\) (worst) | Same as Bubble | Same worst, but fewer on nearly sorted data |
| Swaps / Writes | Up to \(\frac{n^{2}}{2}\) | ≤ \(n-1\) | Up to \(\frac{n^{2}}{2}\) shifts |
| Stability | ✅ | ❌ (unless shifted) | ✅ |
| Adaptivity | ✅ (early‑exit) | ❌ | ✅ (shifts stop early) |
| Typical best case | \(Θ(n)\) | \(Θ(n^{2})\) | \(Θ(n)\) |
| When to prefer | Very small or already sorted arrays, teaching | Write‑cost‑sensitive environments, predictable swap count | Incremental data, nearly sorted arrays |

---

## Tradeoffs / When NOT to Use  

* **Large datasets** – All three degrade to \(Θ(n^{2})\); prefer \(Θ(n\log n)\) algorithms (merge, quick, heap).  
* **High write‑cost memory** – Bubble and Insertion may cause many writes; Selection is better, but still inferior to specialized write‑optimal sorts (e.g., cycle sort).  
* **Stability requirement** – Use Bubble or Insertion; Selection needs extra work.  
* **Real‑time constraints** – Non‑adaptive Selection can’t guarantee early finish on nearly sorted input, making it unsuitable for latency‑sensitive scenarios.  

---

## Interview Q&A  

1. **Implement Bubble Sort with early‑exit. What is its best‑case complexity?**  
   *Answer*: The algorithm stops after the first pass when no swap occurs, performing only \(n-1\) comparisons → \(Θ(n)\) time.  

2. **Why does Selection Sort perform fewer writes than Bubble Sort?**  
   *Answer*: It swaps only once per outer iteration (at most \(n-1\) swaps), whereas Bubble may swap on every inversion, leading to up to \(\frac{n^{2}}{2}\) writes.  

3. **Show how to make Selection Sort stable without changing its \(Θ(n^{2})\) bound.**  
   *Answer*: After locating the minimum, instead of swapping, shift all elements between the current position \(i\) and `minIdx` right by one and place the minimum at \(i\). The number of element moves stays \(Θ(n^{2})\).  

4. **Given an almost‑sorted array, which quadratic sort is expected to finish fastest and why?**  
   *Answer*: Insertion Sort, because it only shifts elements until the correct spot is found; the number of shifts is proportional to the distance each element is out of place, often far less than the full \(n^{2}\) work of Bubble or Selection.  

5. **How would you adapt Selection Sort for a linked list to avoid costly index‑based swaps?**  
   *Answer*: Traverse the list to find the node with the minimum key, then relink it to the front of the unsorted portion (removing it from its original position). This uses only pointer updates, preserving the \(Θ(n^{2})\) comparison count while eliminating array‑style swaps.  

*Follow‑up example*: Implement the linked‑list version and analyze its write count compared to the array version.

---

## Common Misconceptions  

| Misconception | Reality |
|---------------|---------|
| “Bubble Sort is fast because it swaps adjacent items.” | Swapping adjacent items still costs \(Θ(1)\) each; the algorithm makes \(Θ(n^{2})\) swaps in the worst case, so it is slow for any moderate \(n\). |
| “Selection Sort’s \(Θ(n^{2})\) time means it also does \(Θ(n^{2})\) swaps.” | It does at most \(n-1\) swaps; the quadratic cost comes from the comparisons, not the writes. |
| “Insertion Sort always beats Bubble Sort.” | Not always; on reverse‑sorted data both perform \(Θ(n^{2})\) work, but Bubble may have slightly more swaps. However, Insertion’s inner loop stops early on partially sorted data, giving it an advantage in practice. |
| “All three sorts are unstable.” | Only Selection Sort is unstable by default; Bubble and Insertion are naturally stable because they only move elements past larger ones. |
| “Because they are simple, they are acceptable for production code on large inputs.” | Simplicity does not outweigh the quadratic growth; production systems use \(Θ(n\log n)\) algorithms for anything beyond trivial sizes. |

<!-- END -->
