---
topic: Counting Sort, Radix Sort, Bucket Sort
domain: dsa
subtopics: ["non-comparison based sorting"]
sources:
  - title: "Wikipedia: Counting sort"
    url: https://en.wikipedia.org/wiki/Counting_sort
    license: CC BY-SA 4.0
status: NEEDS_HUMAN
open_issues: 1
generator: openai/gpt-oss-120b
critic: openai/gpt-oss-20b
last_verified: 2026-10-02
human_reviewed: false
---
## Definition

**Non‑comparison based sorting** refers to sorting techniques that do not rely on pairwise element comparisons. Instead they exploit properties of the keys—such as integer value, digit representation, or numeric range—to place items directly into their final positions. The three classic members are **Counting Sort**, **Radix Sort**, and **Bucket Sort**. All three achieve linear‑time performance under suitable assumptions, bypassing the Ω(n log n) lower bound that applies to comparison sorts.

---

## How It Works

### Counting Sort  
**Mechanism** – Counting Sort builds a histogram of key frequencies, converts it to a prefix‑sum array that tells where each key’s block starts in the output, and then places each element into that block while preserving stability.

**Worked example** – Sort `A = [4, 2, 2, 8, 3, 3, 1]`.  
1. `k = 8`; allocate `C[0…8] = 0`.  
2. Count pass → `C = [0,1,2,0,1,0,0,0,1]`.  
3. Prefix sum → `C = [0,1,3,3,4,4,4,4,5]`.  
4. Scan `A` right‑to‑left:  
   - element 1 → `C[1]=1 → place at B[0]`, `C[1]←0`  
   - element 3 → `C[3]=3 → B[2]=3`, `C[3]←2`  
   - element 3 → `C[3]=2 → B[1]=3`, `C[3]←1`  
   - element 8 → `C[8]=5 → B[4]=8`, `C[8]←4`  
   - element 2 → `C[2]=3 → B[2]=2`, `C[2]←2` …  
Result `B = [1, 2, 2, 3, 3, 4, 8]`.

### Radix Sort (LSD)  
**Mechanism** – Radix Sort processes keys digit by digit, from least‑significant to most‑significant, using a stable sorter (usually Counting Sort) on each digit. After the final digit pass the whole array is sorted.

**Worked example** – Sort decimal numbers `A = [329, 457, 657, 839, 436, 720, 355]`.  
Base `b = 10`, max digits `d = 3`.  

| Pass | Digit (10⁰) | Counting‑sort result |
|------|-------------|----------------------|
| 1 (units) | 9,7,7,9,6,0,5 | `[720, 355, 436, 457, 329, 657, 839]` |
| 2 (tens)  | 2,5,5,3,3,2,5 | `[720, 329, 436, 457, 355, 657, 839]` |
| 3 (hundreds) | 7,3,4,8,3,6,3 | `[329, 355, 436, 457, 657, 720, 839]` |

The final array is sorted.

### Bucket Sort  
**Mechanism** – Bucket Sort distributes elements into a fixed number of “buckets” that each hold a sub‑range of the key space (often using linked lists or dynamic arrays). After distribution, each bucket is sorted individually (commonly with insertion sort) and concatenated.

**Worked example** – Sort `A = [0.78, 0.17, 0.39, 0.26, 0.72, 0.94, 0.21, 0.12, 0.23, 0.68]` assuming keys lie in `[0,1)`.  
1. Choose `n = 10` buckets → bucket width `0.1`.  
2. Distribute:  
   - bucket 0: `0.12, 0.17`  
   - bucket 1: `0.21, 0.23, 0.26`  
   - bucket 2: `0.39`  
   - bucket 3: `0.68, 0.72, 0.78`  
   - bucket 4: `0.94`  
3. Sort each bucket (insertion sort).  
4. Concatenate → `[0.12, 0.17, 0.21, 0.23, 0.26, 0.39, 0.68, 0.72, 0.78, 0.94]`.

---

## Complexity

| Algorithm | Time | Extra Space | Stability |
|-----------|------|-------------|-----------|
| Counting Sort | **Θ(n + k)** (k = max key) | Θ(n + k) (output + count) | Yes |
| Radix Sort (LSD) | **Θ(d · (n + b))** where *d* = digits, *b* = base | Θ(n + b) per pass | Yes |
| Bucket Sort | Expected **Θ(n + m)** where *m* = number of buckets (often Θ(n)) | Θ(n + m) (buckets + input) | Depends on bucket‑sort routine (usually stable) |

All three are linear‑time only when their auxiliary parameters (k, d·b, m) are O(n).

---

## Key Properties

* **Counting Sort** – Requires integer keys in a known bounded range; inherently stable; space proportional to range size.  
* **Radix Sort** – Works on fixed‑length keys (integers, strings, floating‑point) by treating them as digit sequences; stability comes from the inner counting sort; number of passes equals key length.  
* **Bucket Sort** – Assumes keys are uniformly distributed over a known interval; average‑case linear time; performance degrades if many items fall into few buckets.

---

## Real‑World Use

* **Counting Sort** – Histogram generation, sorting ages or exam scores, as the digit‑level sorter in LSD radix sort for 32‑bit integers.  
* **Radix Sort** – Large‑scale integer sorting in databases, network packet ordering, string sorting (e.g., sorting fixed‑length IDs).  
* **Bucket Sort** – Sorting floating‑point numbers in graphics pipelines, external‑memory sorting where data is roughly uniformly spread, parallel sorting frameworks that assign each bucket to a thread.

---

## Comparison

| Criterion | Counting Sort | Radix Sort | Bucket Sort |
|-----------|---------------|------------|-------------|
| Key type | Small integer range | Fixed‑length digit representation | Real numbers in known interval |
| Best when | k ≈ n | d is small, base chosen to fit cache | Data uniformly distributed |
| Memory overhead | O(k) extra | O(b) per pass | O(n) for bucket containers |
| Parallelizability | Easy (independent count arrays) | Very parallel (each digit pass independent) | Natural (buckets processed independently) |
| Typical libraries | Used internally by radix implementations | Stand‑alone in high‑performance libs | Rarely exposed as a public API |

---

## Tradeoffs / When NOT to Use

* **Counting Sort** – Avoid if the key range is huge (e.g., sorting 32‑bit integers with k ≈ 2³²) because memory blows up and time becomes Θ(k).  
* **Radix Sort** – Not ideal for variable‑length keys with large *d* (e.g., long strings) because the number of passes grows, and the constant factor of counting sort per pass can outweigh O(n log n) comparison sorts.  
* **Bucket Sort** – Poor choice when the key distribution is skewed; many elements may land in a few buckets, causing those buckets to become costly to sort (worst‑case O(n²) if insertion sort is used).

---

## Interview Q&A

1. **Q:** *Implement counting sort for an array that may contain negative integers.*  
   **A:** Find `min` and `max`, shift each key by `-min` to make them non‑negative, allocate `C[0…max‑min]`, run the standard three‑phase algorithm, then shift back when writing to output.  
   **Follow‑up:** *What is the time and space complexity after the shift?* – Still Θ(n + k) where `k = max‑min`.

2. **Q:** *Why does counting sort need to scan the input from right to left in the placement phase?*  
   **A:** Scanning right‑to‑left ensures that equal keys are placed in reverse order of appearance, preserving the original relative order → stability.  
   **Follow‑up:** *If we scanned left‑to‑right, would the algorithm still be correct?* – It would produce a sorted array but would be unstable.

3. **Q:** *Explain how radix sort achieves O(d·(n+b)) time and why it is not O(n log n).*  
   **A:** Each of the `d` digit passes runs counting sort in Θ(n + b). Since `d` is the number of digits (log₍b₎ M) and `b` is a constant (often 256), the total is linear in `n`. The lower bound for comparison sorts does not apply because radix sort never compares keys directly.  
   **Follow‑up:** *What happens to the complexity if we choose a very small base, e.g., b = 2?* – `d` grows (≈ log₂ M), increasing total work; still linear but with larger constant factor.

4. **Q:** *In bucket sort, why is the assumption of uniform distribution important?*  
   **A:** Uniform distribution makes each bucket receive O(n/m) items, giving expected linear time when each bucket is sorted with an O(k²) algorithm like insertion sort. Skewed data can cause one bucket to hold Θ(n) items, degrading to quadratic time.  
   **Follow‑up:** *How can you mitigate this risk?* – Use more buckets, adapt bucket boundaries, or switch to a different internal sorter (e.g., quicksort) for heavy buckets.

5. **Q:** *Compare the space usage of counting sort vs. bucket sort for sorting 1 million integers in the range 0‑999.*  
   **A:** Counting sort needs a count array of size 1 000 plus an output array of size 1 million → ≈ 1 001 k entries. Bucket sort would allocate 1 million buckets (or a smaller number) each holding a list; overhead is larger due to pointer storage. Hence counting sort is more space‑efficient for small ranges.  
   **Follow‑up:** *If the range were 0‑1 billion, which algorithm would you prefer?* – Bucket sort (or another comparison sort) because counting sort’s count array would be prohibitive.

---

## Common Misconceptions

* **“All non‑comparison sorts are always O(n).”** – The hidden parameters (range `k`, number of digits `d`, bucket count `m`) appear in the bounds; large values make the algorithms super‑linear.  
* **“Counting sort is in‑place.”** – The classic version uses a separate output array; an in‑place variant exists but sacrifices stability.  
* **“Radix sort works on any data type.”** – It requires a fixed‑length representation that can be decomposed into digits (e.g., integers, fixed‑size strings). Variable‑length keys need extra handling.  
* **“Bucket sort guarantees linear time.”** – Only under the assumption of uniform distribution; otherwise worst‑case can be quadratic.  
* **“Stability is irrelevant for sorting numbers.”** – Stability matters when the sort is a sub‑routine (e.g., radix sort) or when secondary attributes must be preserved.

<!-- END -->
