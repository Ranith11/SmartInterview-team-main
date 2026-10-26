---
topic: Composite Index
domain: dbms
subtopics: ["column ordering", "selectivity", "covering index"]
sources:
  - title: "Wikipedia: S&P/TSX Composite Index"
    url: https://en.wikipedia.org/wiki/S&P/TSX_Composite_Index
    license: CC BY-SA 4.0
status: NEEDS_HUMAN
open_issues: 2
generator: openai/gpt-oss-120b
critic: openai/gpt-oss-20b
last_verified: 2026-10-02
human_reviewed: false
---
## Definition  

A **composite index** (also called a multi‑column or concatenated index) is a database index that includes more than one column of a table. The index stores a sorted list of the combined values of the indexed columns, allowing the query optimizer to locate rows based on predicates that involve any prefix of the column list. Unlike separate single‑column indexes, a composite index can satisfy queries that filter on several columns simultaneously, often reducing the number of index look‑ups and eliminating the need for additional look‑ups (a “covering” effect).

---

## How It Works  

When a composite index is created, the database engine builds a B‑tree (or similar structure) whose key is the concatenation of the column values in the order specified at creation time. Each leaf entry points to the row’s physical location (row identifier, RID).  

### Column Ordering  

The order of columns in the index key determines which query predicates can be efficiently used. The index can be used for:

* Equality predicates on the leading column(s).  
* Range predicates on the first column that is not tested for equality.  
* Prefix scans that stop as soon as a column without a predicate is encountered.

**Worked example** – Suppose a table `orders(order_id, customer_id, order_date, status)` and a composite index on `(customer_id, order_date)`.  

* Query A: `SELECT * FROM orders WHERE customer_id = 42;` – The index can be used because the leading column (`customer_id`) is constrained by equality. The engine performs a point lookup on the B‑tree leaf range for `customer_id = 42`.  
* Query B: `SELECT * FROM orders WHERE customer_id = 42 AND order_date >= '2024‑01‑01';` – The index can still be used; after locating the first leaf for `customer_id = 42`, the engine scans forward until `order_date` no longer satisfies the range.  
* Query C: `SELECT * FROM orders WHERE order_date >= '2024‑01‑01';` – The index **cannot** be used for the range on `order_date` alone because `customer_id` (the leading column) is not constrained. The optimizer would fall back to a full table scan or a different index.

Thus, column ordering is a design decision that should reflect the most selective and most frequently queried columns first.

### Selectivity  

Selectivity measures how many distinct values a column (or column combination) has relative to the total row count. High selectivity (close to 1.0) means the column filters out many rows; low selectivity (close to 0) means many rows share the same value.  

When building a composite index, the combined selectivity of the leading columns determines how useful the index will be. If the first column is low‑selectivity (e.g., a status flag with only three possible values), the index may still be valuable if the second column adds enough discrimination.

**Worked example** – In a `users` table with columns `country` (≈200 distinct values) and `signup_date` (≈10,000 distinct dates), the combined selectivity of `(country, signup_date)` is higher than either column alone. A query `WHERE country = 'CA' AND signup_date = '2024‑03‑15'` will likely return a small subset, making the composite index efficient. Conversely, an index on `(status, country)` where `status` has only values `('active','inactive')` may be less effective unless `country` is also highly selective and frequently used together with `status`.

### Covering Index  

A composite index becomes a **covering index** when it contains all columns required by a query (both in the `SELECT` list and the `WHERE` clause). In that case, the database can satisfy the query entirely from the index without touching the base table, dramatically reducing I/O.

**Worked example** – Consider a table `sales(product_id, store_id, sale_date, quantity, revenue)`. Create a composite index on `(store_id, sale_date, quantity, revenue)`.  

Query:  

```sql
SELECT quantity, revenue
FROM sales
WHERE store_id = 7 AND sale_date BETWEEN '2024-01-01' AND '2024-01-31';
```

All columns referenced (`store_id`, `sale_date`, `quantity`, `revenue`) are present in the index. The optimizer can perform a range scan on the index for the `store_id` and `sale_date` predicates and return `quantity` and `revenue` directly from the index leaf nodes, avoiding a lookup to the main table rows.

---

## Key Properties  

| Property | Description | Impact on Performance |
|----------|-------------|-----------------------|
| **Column order** | Determines which predicates can be used and the direction of scans. | Misordered columns can render the index useless for common queries. |
| **Combined selectivity** | Product of selectivities of leading columns. | Higher combined selectivity → fewer rows scanned → faster queries. |
| **Covering capability** | Index contains all needed columns. | Eliminates table look‑ups, reduces I/O and CPU. |
| **Size** | Composite indexes are larger than single‑column indexes because each entry stores multiple values. | Larger size → more storage, potentially slower writes (insert/update/delete). |
| **Maintenance cost** | Every data modification must update the index. | High write workloads may suffer if many composite indexes exist. |

---

## Real‑World Use  

* **E‑commerce** – An index on `(category_id, price)` enables fast retrieval of products within a category and price range, while also covering queries that only need `product_name` and `price`.  
* **Analytics** – Data warehouses often create composite indexes on `(region, event_date, metric_id)` to accelerate time‑series reports filtered by region and metric.  
* **Logging systems** – An index on `(log_level, timestamp)` allows quick scans of recent error logs while also covering the `message` column for simple log‑viewer queries.

In each case, the index is chosen to match the most common query patterns, balancing read performance against write overhead.

---

## Comparison  

| Aspect | Composite Index | Multiple Single‑Column Indexes |
|--------|----------------|-------------------------------|
| **Query support** | Handles multi‑column predicates efficiently; can serve as covering index. | May require index intersection or bitmap operations; often less efficient for combined predicates. |
| **Storage** | Larger per‑entry size (stores all columns). | Smaller per‑entry size; total size may be larger if many columns are indexed separately. |
| **Write overhead** | One index to maintain, but each entry is heavier. | Multiple lighter indexes; each write updates all relevant indexes. |
| **Flexibility** | Fixed column order; not useful for predicates that skip the leading column. | More flexible for predicates on any single column. |
| **Covering** | Can cover queries that need only indexed columns. | Rarely covering unless all needed columns happen to be indexed individually. |

---

## Tradeoffs / When NOT to Use  

* **Low selectivity leading column** – If the first column returns a large fraction of rows, the index provides little pruning.  
* **Write‑heavy tables** – Composite indexes increase the cost of inserts/updates because the full key must be maintained.  
* **Sparse query patterns** – If queries rarely combine the same set of columns, a composite index may be wasted space.  
* **Skipping leading column** – Queries that filter only on the second or later column cannot use the index efficiently. In such cases, separate single‑column indexes or a different column order are preferable.  

---

## Interview Q&A  

1. **Q:** *What determines whether a composite index can be used for a given query?*  
   **A:** The optimizer can use the index if the query predicates reference a **prefix** of the indexed columns—i.e., the leading column(s) are constrained by equality or a range, and no predicate appears on a later column without a predicate on all preceding columns.  
   **Follow‑up:** *How would you rewrite a query that filters only on the second column to make use of the index?*  

2. **Q:** *Explain the concept of a covering index and why it is beneficial.*  
   **A:** A covering index contains every column referenced by the query (SELECT list and WHERE clause). The engine can satisfy the query directly from the index leaf pages, avoiding a costly lookup to the base table, which reduces I/O and CPU usage.  
   **Follow‑up:** *Give an example where adding a non‑key column to a composite index turns it into a covering index.*  

3. **Q:** *How does column ordering affect index selectivity?*  
   **A:** The leading column’s selectivity dominates the index’s pruning power. Placing the most selective column first maximizes the chance that the index will filter out many rows early, leading to smaller scans.  
   **Follow‑up:** *If two columns have equal selectivity, what other factors might influence the ordering decision?*  

4. **Q:** *What are the trade‑offs between a composite index and multiple single‑column indexes?*  
   **A:** A composite index excels at queries that filter on the same column combination and can act as a covering index, but it is larger and less flexible for predicates that skip the leading column. Multiple single‑column indexes are smaller and can be combined via bitmap or index‑merge strategies, but they often incur extra processing and rarely cover queries.  
   **Follow‑up:** *When would you prefer a bitmap index merge over a composite index?*  

5. **Q:** *Describe a scenario where a composite index could actually degrade performance.*  
   **A:** In a write‑intensive table where the leading column has low selectivity and most queries filter only on later columns, the composite index adds unnecessary maintenance overhead and provides little read benefit, thus slowing overall performance.  
   **Follow‑up:** *What monitoring metrics would you examine to detect such a problem?*  

---

## Common Misconceptions  

* **“The order of columns doesn’t matter because the optimizer can reorder them.”**  
  *Reality:* The optimizer cannot reorder columns inside a B‑tree index. Only the defined prefix can be used; predicates on later columns without constraints on earlier ones are ignored.  

* **“Adding more columns always makes the index more useful.”**  
  *Reality:* Extra columns increase index size and write cost. If the added columns are rarely queried together, the index becomes a storage burden without performance gain.  

* **“A composite index automatically covers all queries that reference its columns.”**  
  *Reality:* Coverage requires that **all** columns needed by the query (including those in the SELECT list) are present in the index. If a query selects a column not in the index, a table lookup is still required.  

* **“If two single‑column indexes exist, the database will automatically combine them as efficiently as a composite index.”**  
  *Reality:* Index intersection or bitmap merging can be used, but it usually involves extra processing and may not be as fast as a single composite index that matches the query’s predicate order.  

* **“Low selectivity columns should never be part of a composite index.”**  
  *Reality:* A low‑selectivity column can be useful as a leading column if it is frequently used with equality predicates together with a highly selective second column; the combined selectivity may still be high.

<!-- END -->
