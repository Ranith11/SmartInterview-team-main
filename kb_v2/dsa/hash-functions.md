---
topic: Hash Functions
domain: dsa
subtopics: ["division", "multiplication", "universal hashing"]
sources:
  - title: "Wikipedia: Hash function"
    url: https://en.wikipedia.org/wiki/Hash_function
    license: CC BY-SA 4.0
status: AUTO_VERIFIED
open_issues: 0
generator: openai/gpt-oss-120b
critic: openai/gpt-oss-20b
last_verified: 2026-10-02
human_reviewed: false
---
## Definition  

A **hash function** `h` maps a key `k` from an arbitrary universe `U` to a fixed‑size index set `{0,…,m‑1}` that corresponds to the slots of a hash table. Formally, `h : U → {0,…,m‑1}`. The function must be deterministic (the same key always yields the same index) and fast to compute, typically in constant time. In the context of hash tables the function is used to distribute keys uniformly over the `m` buckets so that collisions are rare and average‑case operations are near‑constant.

Three classic families used for non‑cryptographic hashing are:

* **Division method** – uses the remainder of integer division.  
* **Multiplication method** – multiplies the key by a constant and extracts high‑order bits.  
* **Universal hashing** – selects a function at random from a family that guarantees a low collision probability for any pair of distinct keys.

---

## How It Works  

### Division Method  

1. Choose a table size `m`. Good practice is to pick a prime that is not close to a power of two.  
2. Compute `index = k mod m`.  
3. Use `index` as the bucket number.

**Worked example**  
Suppose `m = 13` (prime) and the keys are integers.  

| key `k` | `k mod 13` | bucket |
|--------|------------|--------|
| 27     | 27 mod 13 = 1 | 1 |
| 58     | 58 mod 13 = 6 | 6 |
| 102    | 102 mod 13 = 11| 11 |

Each key is placed in the bucket shown; collisions are resolved with chaining or probing.

---

### Multiplication Method  

1. Let the machine word size be `w` bits (e.g., `w = 32`).  
2. Choose a constant `A` with `0 < A < 2^w`. Knuth recommends `A = ⌊2^w·(√5−1)/2⌋`.  
3. Compute the product `p = (k·A) mod 2^w` (i.e., keep the low `w` bits).  
4. The index is `⌊ m·p / 2^w ⌋`, which is equivalent to taking the high‑order `⌈log₂ m⌉` bits of `p`.

**Worked example**  
Take `w = 32`, `m = 16` (a power of two), and `A = 2654435769` (Knuth’s constant).  

*Key `k = 12345678`*  

```
p = (12345678 × 2654435769) mod 2^32
  = 0x9E3779B9 (decimal 2654435769)   // low 32 bits of the product
index = ⌊ 16 × p / 2^32 ⌋
      = ⌊ 16 × 2654435769 / 4294967296 ⌋
      = ⌊ 9.89 ⌋ = 9
```

Thus key 12345678 maps to bucket 9. The method works for any `m`; the high bits of the product are well‑mixed, giving good uniformity even when `m` is a power of two.

---

### Universal Hashing  

1. Pick a prime `p` larger than any possible key value.  
2. Randomly choose `a ∈ {1,…,p‑1}` and `b ∈ {0,…,p‑1}` once, when the table is created.  
3. Define  

```
h_{a,b}(k) = ((a·k + b) mod p) mod m .
```

4. Use `h_{a,b}` for all insert, lookup, and delete operations.

**Worked example**  
Let `p = 101`, `m = 10`, and randomly chosen parameters `a = 37`, `b = 23`.  

*Key `k = 58`*  

```
temp = (37·58 + 23) mod 101
     = (2146 + 23) mod 101
     = 2169 mod 101 = 46
index = 46 mod 10 = 6
```

Key 58 is placed in bucket 6. Because `a` and `b` are secret random values, an adversary cannot craft a set of keys that all collide; the collision probability for any two distinct keys is at most `1/m`.

---

## Complexity  

| Operation | Division | Multiplication | Universal |
|-----------|----------|----------------|-----------|
| Hash evaluation | **O(1)** – one modulo (division) | **O(1)** – one multiplication + shift | **O(1)** – one multiplication, one addition, two modulo reductions |
| Expected insertion / lookup / delete | **O(1)** (low load factor) | **O(1)** | **O(1)** (expected) |
| Worst‑case (adversarial) | **O(n)** if many keys map to the same bucket | **O(n)** if `A` is poorly chosen or keys are pathological | **O(n)** but probability of a bad cluster ≤ `1/m` per pair |
| Space overhead | Table of size `m` plus collision‑resolution structure | Same as division | Same as division plus constant‑size parameters `(a,b)` |

Division can be slower on modern CPUs because integer division takes many cycles; multiplication is usually faster. Universal hashing adds a tiny constant overhead for the extra parameters but gives provable collision bounds.

---

## Key Properties  

| Property | Division | Multiplication | Universal |
|----------|----------|----------------|-----------|
| **Determinism** | Fixed once `m` is chosen | Fixed once `A` and `m` are chosen | Fixed after random `(a,b)` are selected |
| **Uniformity** | Depends on `m`; poor if `m` shares factors with key distribution | Generally uniform for any `m` because high bits of the product are well‑mixed | Provably uniform in expectation: `Pr[h(x)=h(y)] ≤ 1/m` |
| **Sensitivity to `m`** | Strong – prime `m` reduces clustering | Weak – works for any `m` (including powers of two) | Independent of `m` beyond final modulo |
| **Implementation cost** | One division (potentially expensive) | One multiplication + shift (cheap) | One multiplication, one addition, two modular reductions (mod `p` may be optimized) |
| **Collision resistance (non‑cryptographic)** | None; attacker can force collisions if `m` is known | Better but still deterministic | Stronger because attacker does not know random parameters |
| **Typical use** | Simple educational hash tables, static tables with known size | Production hash tables where `m` is a power of two (e.g., Java’s `HashMap`) | Randomized algorithms, Cuckoo hashing, Bloom‑filter families, situations requiring provable bounds |

---

## Real‑World Use  

* **Division method** – Early C library hash tables and many textbook examples use a prime table size and `key mod prime`.  
* **Multiplication method** – The classic “Knuth multiplicative hash” is used in low‑level libraries (e.g., the Linux kernel’s `hash_32` macro) and in Java’s `HashMap` secondary hashing step.  
* **Universal hashing** – Core of Cuckoo hashing implementations, the hash families behind Bloom filters, and randomized data‑structure libraries such as Google’s `dense_hash_map`. It is also the theoretical foundation for perfect hashing schemes.

---

## Comparison  

| Aspect | Division | Multiplication | Universal |
|--------|----------|----------------|-----------|
| **Speed** | Slower on CPUs lacking fast division | Fast – single multiply & shift | Slightly slower than plain multiplication due to extra modulo |
| **Ease of implementation** | Very simple | Simple, but requires a good constant `A` | Requires random parameter generation and a prime `p` |
| **Uniformity guarantee** | Heuristic; depends on choice of `m` | Good in practice for any `m` | Formal guarantee (`≤ 1/m` collision probability) |
| **Robustness to adversarial keys** | Weak – attacker can choose keys that all map to the same bucket | Better but still deterministic | Strong – attacker cannot predict the random parameters |
| **When to prefer** | Small, static tables where division cost is negligible | Large tables where `m` is a power of two and speed matters | Applications that need provable bounds or resist malicious inputs |

---

## Tradeoffs / When NOT to Use  

* **Division** – Avoid when the target platform has a costly integer division unit or when the table size must be a power of two (division loses the uniformity benefit).  
* **Multiplication** – Poor choice if the constant `A` is chosen arbitrarily; a bad `A` can create patterns for certain key distributions. Also unsuitable when cryptographic‑level randomness is required.  
* **Universal hashing** – Overkill for simple in‑memory hash tables with benign key distributions; the extra random‑parameter generation and modulo‑`p` operations add overhead. Not ideal when deterministic reproducibility of hash codes across runs is required (e.g., serialization formats).

---

## Interview Q&A  

1. **Q:** *Why is a prime table size recommended for the division method?*  
   **A:** A prime `m` reduces the chance that common factors between the key distribution and `m` cause systematic clustering. When `m` is prime, the mapping `k mod m` behaves more like a random permutation of the residues, improving uniformity.  
   **Follow‑up:** *What happens if `m` is a power of two?* – Keys that differ only in higher bits will collide, leading to many collisions for low‑entropy keys.

2. **Q:** *Explain how the multiplication method achieves uniform distribution regardless of `m`.*  
   **A:** Multiplication mixes the bits of the key by scaling it with an irrational‑like constant `A`. The high‑order bits of the product are effectively a pseudo‑random function of the key, and extracting those bits yields a value that is uniformly distributed for any `m`.  
   **Follow‑up:** *What constant does Knuth suggest and why?* – `A = ⌊2^w·(√5−1)/2⌋`; it approximates the fractional part of the golden ratio, which has good mixing properties.

3. **Q:** *What is universal hashing and what guarantee does it provide?*  
   **A:** Universal hashing selects a hash function at random from a family such that for any two distinct keys `x ≠ y`, the probability of a collision is at most `1/m`. This gives an expected collision rate identical to that of a truly random function, independent of the key distribution.  
   **Follow‑up:** *How does this help against adversarial inputs?* – An attacker cannot predict the random parameters, so they cannot craft a set of keys that all collide.

4. **Q:** *Compare the runtime cost of division vs. multiplication on modern CPUs.*  
   **A:** Integer division typically takes many more cycles (10–30) than a single integer multiply (1–3 cycles). Consequently, the multiplication method is usually faster, especially in tight loops.  
   **Follow‑up:** *Can division be avoided entirely?* – Yes, by using multiplication by the modular inverse of a constant or by the multiplication method itself.

5. **Q:** *When would you choose universal hashing over the simpler multiplication method?*  
   **A:** When the application may face maliciously chosen keys (e.g., hash‑table DoS attacks) or when provable expected‑case bounds are required, such as in randomized algorithms or Cuckoo hashing.  
   **Follow‑up:** *What extra space does universal hashing need?* – Only the constant parameters `(a,b)` (and the prime `p` if not hard‑coded), which is O(1) extra space.

---

## Common Misconceptions  

* **“A hash function must be cryptographically secure.”** – For hash tables we need speed and low collision probability, not cryptographic hardness. Non‑cryptographic functions (division, multiplication) are perfectly acceptable.  
* **“Multiplication works only when the table size is a power of two.”** – The method works for any `m`; the high‑order bits are taken after scaling, so `m` can be arbitrary.  
* **“Universal hashing eliminates all collisions.”** – It only guarantees a low *expected* collision probability (`≤ 1/m`). Collisions can still occur; a collision‑resolution strategy is still required.  
* **“Choosing a large constant `A` in the multiplication method always improves distribution.”** – The constant must be carefully chosen (e.g., Knuth’s golden‑ratio constant). Arbitrary large values can produce poor mixing or overflow patterns.  
* **“If I use a prime `m`, the division method is always optimal.”** – Uniformity also depends on the key distribution; a prime `m` mitigates but does not guarantee optimal performance.

<!-- END -->
