---
topic: Indexing: B-Tree Index, Hash Index, Bitmap Index, Full-Text Index
domain: dbms
subtopics: []
sources:
  - title: "Wikipedia: Database index"
    url: https://en.wikipedia.org/wiki/Database_index
    license: CC BY-SA 4.0
status: NEEDS_HUMAN
open_issues: 5
generator: openai/gpt-oss-120b
critic: openai/gpt-oss-20b
last_verified: 2026-10-02
human_reviewed: false
---
## Definition  

A database index is a auxiliary data structure that stores a copy of one or more column values together with a pointer to the original row.  By keeping the keys in a searchable order (or in a hash‑able form) the index lets the DBMS locate matching rows in sub‑linear time instead of scanning the whole table.  Different index types trade off lookup speed, update cost, storage size and the kinds of predicates they can accelerate.  The four most common families are **B‑Tree indexes**, **Hash indexes**, **Bitmap indexes**, and **Full‑Text indexes**.

---

## How It Works  

### B‑Tree Index  

A B‑Tree (usually a B⁺‑Tree) is a balanced multi‑way search tree.  Every internal node contains up to *m* keys and *m + 1* child pointers; leaf nodes store the indexed key values in sorted order together with a row identifier (RID).  Because the tree is height‑balanced, the number of node hops from root to leaf is *O(logₘ N)*, where *N* is the number of indexed rows.

**Worked example** – Suppose a table `Employees(id INT PRIMARY KEY, name VARCHAR)` has 1 000 000 rows and we create a B‑Tree index on `id`.  With a fan‑out *m* = 100, the tree height is ⌈log₁₀₀ 1 000 000⌉ = 3.  To find `id = 527 342` the engine:

1. Reads the root (contains key ranges, e.g., 0‑199 999, 200 000‑399 999, …).  
2. Follows the child pointer for the range 400 000‑599 999.  
3. Reads the second‑level node, selects the child covering 520 000‑539 999.  
4. Reads the leaf page, scans the few entries until it finds 527 342, then follows the RID to the data page.

Only three I/O operations are needed regardless of the table size.

### Hash Index  

A hash index applies a deterministic hash function *h(k)* to the indexed key *k* and stores the resulting bucket number in a hash table.  Each bucket holds a list (or overflow page) of RIDs whose keys hash to the same value.  Look‑up is constant‑time *O(1)* on average because the bucket is located directly from the hash value; collisions are resolved by chaining or open addressing.

**Worked example** – For a `Customers(email VARCHAR)` column we use a simple modulo hash: `bucket = CRC32(email) mod 1024`.  Inserting `alice@example.com` yields bucket = 237; the RID (page = 45, slot = 12) is appended to bucket 237’s list.  To find the same email, the engine recomputes the hash, jumps straight to bucket 237, and scans the short list (usually 1–2 entries).  No tree traversal is required.

### Bitmap Index  

A bitmap index stores, for each distinct value *v* of a low‑cardinality column, a bit‑vector *Bᵥ* whose *i*‑th bit is 1 iff row *i* contains *v*.  Queries combine these vectors with fast bitwise operators (AND, OR, NOT).  Because the vectors are highly compressible (run‑length or word‑aligned compression), the index can be tiny even for millions of rows.

**Worked example** – In a `Products(gender_target CHAR)` column with values {‘M’, ‘F’, ‘U’}, three bitmaps are built for 10 000 rows:

```
B_M = 100100… (1 where gender = 'M')
B_F = 010010… 
B_U = 001001…
```

A query `WHERE gender_target IN ('M','F')` is answered by `B_M OR B_F`, producing a single bitmap that directly marks the qualifying rows.  No row‑by‑row comparison is needed.

### Full‑Text Index  

Full‑text indexes are inverted indexes that map each token (word, trigram, etc.) to the list of document identifiers that contain it.  The DBMS tokenizes the indexed text column, optionally applies stemming or stop‑word removal, and stores posting lists (often in a B‑Tree or GIN structure).  Queries such as `WHERE CONTAINS(body, 'database')` intersect the posting lists for the searched terms.

**Worked example** – A table `Articles(id, body)` is indexed with a trigram GIN index.  The phrase “database indexing” yields trigrams `{'dat', 'ata', 'tab', 'aba', 'bas', 'asi', 'sin', 'ing'}`.  The engine retrieves the posting list for each trigram, intersects them, and returns the article IDs that contain all trigrams, achieving roughly *O(log N)* lookup instead of a full scan.

---

## Complexity  

| Index Type | Lookup | Insert / Update | Space |
|------------|--------|----------------|-------|
| B‑Tree     | *O(log N)* (height of tree) | *O(log N)* (node split/merge) | O(N) pointers + keys |
| Hash       | *O(1)* average, *O(N)* worst (hash collision) | *O(1)* average (rehash occasional) | O(N) buckets |
| Bitmap     | *O(1)* bitwise ops (after bitmap fetch) | *O(N/word‑size)* to set/clear bits | O(N × cardinality) (compressed) |
| Full‑Text  | *O(log N + k)* where *k* = size of posting list | *O(L log N)* where *L* = number of tokens | O(total tokens) |

---

## Key Properties  

| Property | B‑Tree | Hash | Bitmap | Full‑Text |
|----------|--------|------|--------|-----------|
| Order‑preserving (range scans) | ✅ | ❌ | ❌ | ✅ (via posting list order) |
| Equality look‑up | ✅ | ✅ | ✅ (via bitmap) | ✅ (term match) |
| Low‑cardinality suitability | ❌ (many duplicates) | ✅ (if hash distributes) | ✅ (designed for few distinct values) | ✅ (text tokens) |
| Concurrency friendliness | Well‑studied lock‑coupling | Simple latch per bucket | Mostly read‑only, good for OLAP | Complex due to posting‑list updates |
| Update cost | Moderate (node splits) | Low (bucket append) | Moderate (bit flips) | High (token insertion) |

---

## Real‑World Use  

* **B‑Tree** – Default index for primary keys, foreign keys, and most `WHERE` predicates that involve range conditions (`BETWEEN`, `>`, `<`).  All major RDBMS (PostgreSQL, MySQL InnoDB, Oracle) use B‑Trees for non‑clustered indexes.  
* **Hash** – Used in memory‑only engines (e.g., PostgreSQL’s hash indexes, MySQL MEMORY) and for hash‑partitioned tables where equality look‑ups dominate.  
* **Bitmap** – Favoured in data‑warehousing systems (Oracle Bitmap Indexes, PostgreSQL’s `BITMAP` extension) where columns have few distinct values and queries involve many simultaneous predicates.  
* **Full‑Text** – Implemented as GIN or GiST indexes in PostgreSQL, as `FULLTEXT` indexes in MySQL, and as `CONTAINS` indexes in SQL Server for searching large text fields, email bodies, or product descriptions.

---

## Comparison  

| Scenario | Best Index | Why |
|----------|------------|-----|
| Find a single row by primary key | B‑Tree (clustered) | Guarantees *O(log N)* and keeps rows physically ordered. |
| Equality search on a high‑cardinality column in an in‑memory table | Hash | Direct bucket access gives constant time. |
| Filtering on several low‑cardinality columns (e.g., gender, status) in a reporting query | Bitmap | Bitwise AND/OR merges many predicates efficiently. |
| Searching for words or phrases inside large text blobs | Full‑Text (inverted) | Token → document mapping avoids scanning the whole column. |
| Range scan on dates with occasional point look‑ups | B‑Tree | Supports both equality and ordered scans. |

---

## Tradeoffs / When NOT to Use  

* **B‑Tree** – Not ideal for columns with extremely low cardinality (many duplicates) because the tree becomes shallow and leaf pages are under‑utilized.  
* **Hash** – Cannot serve range queries; performance degrades sharply if the hash function causes many collisions or if the table grows beyond the initial bucket count (rehashing is expensive).  
* **Bitmap** – Poor choice for high‑cardinality columns (e.g., UUID) because the bitmap would be huge; also heavy on write‑intensive workloads because each row change flips many bits.  
* **Full‑Text** – Overkill for exact‑match or short‑string searches; index build and maintenance are costly, and the index size can be large for massive corpora.

---

## Interview Q&A  

1. **Q:** *Why do most relational databases use B‑Tree indexes for primary keys?*  
   **A:** B‑Trees keep keys sorted, enabling both fast equality look‑ups (*O(log N)*) and efficient range scans, which are essential for primary‑key look‑ups and ordered queries. They also allow the leaf pages to store the actual row data in a clustered index, reducing I/O.  
   **Follow‑up:** *What happens to performance if the primary key column has many duplicate values?*  

2. **Q:** *Explain how a hash index achieves O(1) lookup.*  
   **A:** The index applies a deterministic hash function to the search key, producing a bucket number. The bucket directly points to the list of matching RIDs, so the engine jumps to the bucket without traversing a tree. The average case is constant time; worst‑case collisions can degrade to linear time.  
   **Follow‑up:** *How does the DBMS handle bucket overflow?*  

3. **Q:** *When would you prefer a bitmap index over a B‑Tree?*  
   **A:** When the indexed column has very low cardinality (few distinct values) and queries combine many such columns with AND/OR predicates. Bitmap indexes compress repeated values into bitmaps, allowing fast bitwise operations that outperform B‑Tree scans.  
   **Follow‑up:** *Why are bitmap indexes less suitable for OLTP workloads?*  

4. **Q:** *Describe the structure of a full‑text (inverted) index and how a multi‑term query is processed.*  
   **A:** The index stores a posting list for each token, mapping the token to the set of document IDs containing it. For a query with terms *t₁, t₂*, the engine retrieves the two posting lists and computes their intersection (or union, depending on the operator) to obtain the matching documents. The posting lists are often kept in a B‑Tree or GIN for fast retrieval.  
   **Follow‑up:** *How does stemming affect the size of the posting lists?*  

5. **Q:** *What are the main factors that influence the choice of fan‑out (order) in a B‑Tree index?*  
   **A:** The fan‑out is determined by the page size and the size of each key‑pointer pair. Larger fan‑out reduces tree height (fewer I/O hops) but may waste space if keys are small. DBMSs typically choose the maximum number of entries that fit in a disk page to balance depth and space utilization.  
   **Follow‑up:** *If you double the page size, how does the expected tree height change?*  

---

## Common Misconceptions  

* **“Hash indexes are always faster than B‑Trees.”**  
  Hashes give O(1) look‑ups only for pure equality predicates. They cannot handle range scans, and poor hash distribution or heavy collisions can nullify the advantage.

* **“Bitmap indexes are just compressed B‑Trees.”**  
  Bitmap indexes store whole columns as bit vectors, not as sorted key‑pointer pairs. Their strength lies in set‑based logical operations, not in ordered traversal.

* **“Full‑text indexes replace normal indexes for all string columns.”**  
  Full‑text indexes are optimized for token search, not for exact matches or prefix searches. Using them for simple equality checks wastes space and adds unnecessary complexity.

* **“A clustered B‑Tree index automatically speeds up every query on the table.”**  
  Only queries that can exploit the physical ordering (range scans, primary‑key look‑ups) benefit. Queries on unrelated columns still need separate non‑clustered indexes.

* **“Adding more indexes always improves read performance.”**  
  Each additional index incurs write overhead (updates must modify every index) and consumes storage. Over‑indexing can degrade overall throughput, especially in write‑heavy workloads.

<!-- END -->
