---
topic: CAP Theorem applied to NoSQL databases
domain: dbms
subtopics: ["CP vs AP systems", "examples"]
sources:
  - title: "Wikipedia: NoSQL"
    url: https://en.wikipedia.org/wiki/NoSQL
    license: CC BY-SA 4.0
status: NEEDS_HUMAN
open_issues: 4
generator: openai/gpt-oss-120b
critic: openai/gpt-oss-20b
last_verified: 2026-10-02
human_reviewed: false
---
## Definition  

The **CAP theorem** (Consistency, Availability, Partition tolerance) states that a distributed data store can guarantee at most two of these three properties simultaneously. In the context of NoSQL databases, systems are often classified by the trade‑off they make during a network partition:

* **CP (Consistency + Partition tolerance)** – the system refuses to serve a request that cannot be guaranteed to be consistent when a partition occurs.  
* **AP (Availability + Partition tolerance)** – the system continues to serve requests even when some replicas cannot communicate, accepting that reads may return stale data (eventual consistency).

NoSQL databases deliberately choose one side of the trade‑off to meet the scalability and latency requirements of modern web‑scale applications.

---

## How It Works  

### CP vs AP systems  

| Property | CP (e.g., HBase, MongoDB with strong write concern) | AP (e.g., Cassandra, DynamoDB) |
|----------|---------------------------------------------------|--------------------------------|
| **Consistency** | Guarantees that a read returns the most recent write that was acknowledged. During a partition, the system may block reads/writes on the isolated side. | Guarantees that a read will succeed, but the value may be stale until replicas converge (eventual consistency). |
| **Availability** | May reject requests when a quorum cannot be formed, sacrificing availability to preserve consistency. | Always returns a response, even if some replicas are unreachable. |
| **Partition tolerance** | Both CP and AP must tolerate partitions; the difference is how they react. |

**Mechanism (CP example – quorum writes):**  
1. Client issues a write with a *majority* quorum (`W = floor(N/2)+1`).  
2. Coordinator forwards the write to all replicas.  
3. The write is considered successful only after `W` replicas acknowledge.  
4. If a partition isolates enough replicas that `W` cannot be reached, the coordinator returns an error, preserving consistency.

**Mechanism (AP example – hinted handoff):**  
1. Client writes to the local node; the node stores the write locally.  
2. If some replicas are unreachable, the node records a *hint* indicating which replica missed the update.  
3. When the partition heals, the node forwards the hinted updates to the missing replicas, achieving eventual consistency.

### Examples  

**CP Example – Apache HBase:**  
HBase stores data in a distributed, column‑family store built on top of Hadoop HDFS. It uses a *strictly consistent* read‑write path: a client must contact the region server that holds the primary copy of a row. If the primary region server is unavailable due to a partition, the client receives an error rather than a possibly stale value.

*Worked numeric example:*  
Assume a table with replication factor `N = 3`. A client writes value `V = 42` to row `R`. The write is only acknowledged after the primary and at least one secondary replica confirm (`W = 2`). If a network split isolates the primary, the client cannot reach `W = 2` replicas, so the write fails. Any subsequent read will either return the previous committed value or an error, never a partially written state.

**AP Example – Apache Cassandra:**  
Cassandra replicates data across multiple nodes using a *tunable* consistency model. With `CONSISTENCY ONE`, a write is considered successful after a single replica stores it. Reads can also be served from any replica. During a partition, each side continues to accept writes; later, *read‑repair* and *anti‑entropy* (Merkle tree) processes reconcile differences.

*Worked numeric example:*  
Replication factor `N = 3`, client writes `V = 99` to key `K` with consistency `ONE`. The write lands on node A (partitioned side). Meanwhile, node B on the other side also receives a write `V = 100` for the same key. Both writes succeed. After the partition heals, Cassandra’s *last‑write‑wins* (based on timestamps) resolves the conflict, and all replicas converge to the later timestamp value.

---

## Key Properties  

| Property | CP Systems | AP Systems |
|----------|------------|------------|
| **Strong consistency** | Yes (reads see latest committed write) | No – only eventual consistency |
| **Read latency during partitions** | May be high or fail | Low – reads always succeed |
| **Write latency during partitions** | May be high or fail | Low – writes succeed locally |
| **Conflict resolution** | Rarely needed for reads; write‑write conflicts still require resolution (e.g., timestamps) | Required for divergent writes; mechanisms include timestamps, vector clocks, or custom merge functions |
| **Typical replication factor** | Often 3, with quorum reads/writes (`R + W > N`) | Often 3, with tunable `R` and `W` (e.g., `ONE`, `QUORUM`) |
| **Use‑case focus** | Financial transactions, inventory systems where stale reads are unacceptable | Social feeds, IoT telemetry, caching layers where availability outweighs immediate consistency |

---

## Real‑World Use  

* **CP – HBase / Google Bigtable** – Used for large‑scale analytics where a consistent view of data is critical (e.g., ad‑click logs that must not double‑count).  
* **CP – MongoDB with “majority” write concern** – Employed in e‑commerce order processing to guarantee that an order is either fully recorded or rejected.  
* **AP – Cassandra** – Powers messaging platforms (e.g., Instagram) where users expect low latency even under network glitches.  
* **AP – DynamoDB** – Back‑ends serverless applications that need to stay online despite occasional partitions; eventual consistency is acceptable for many user‑profile reads.  

These deployments illustrate how the CAP choice aligns with business priorities: strict correctness vs. uninterrupted service.

---

## Comparison  

| Aspect | CP (e.g., HBase) | AP (e.g., Cassandra) |
|--------|------------------|----------------------|
| **Failure mode** | Requests may be rejected → higher error rate during partitions | Requests succeed → higher stale‑read rate |
| **Data model impact** | Often column‑family or document with strong write guarantees; schema may be more normalized to avoid cross‑node joins | Denormalization is common to avoid cross‑node coordination; data is duplicated across replicas |
| **Operational complexity** | Need to monitor quorum health; may require manual failover handling | Need to manage repair processes (e.g., `nodetool repair`) to keep replicas in sync |
| **Throughput** | Slightly lower under normal conditions due to quorum overhead | Higher write throughput because only one replica is needed for acknowledgment |

---

## Tradeoffs / When NOT to Use  

* **Do NOT choose CP** when your application cannot tolerate request failures, such as a public‑facing social feed where a brief error would degrade user experience.  
* **Do NOT choose AP** for systems that require strict regulatory compliance (e.g., banking ledgers) where stale reads could cause legal violations.  
* Avoid CP if your deployment spans highly unreliable networks (e.g., edge devices) because frequent partitions would cause many rejected operations.  
* Avoid AP if your data model relies heavily on real‑time aggregates that must be accurate at read time; eventual convergence may produce incorrect analytics.

---

## Interview Q&A  

1. **Q:** *What does the CAP theorem state, and why must a distributed NoSQL system choose between CP and AP?*  
   **A:** CAP says a distributed system can guarantee at most two of Consistency, Availability, and Partition tolerance simultaneously. Since partitions are inevitable in large clusters, a system must decide whether to preserve Consistency (CP) or Availability (AP) when a partition occurs.  
   **Follow‑up:** *Can a system change its choice at runtime?*  
   **A:** No. The trade‑off is baked into the protocol; a node cannot be both CP and AP during the same partition.

2. **Q:** *Explain how a quorum write works in a CP system.*  
   **A:** The client specifies a write quorum `W`. The coordinator forwards the write to all replicas and waits for acknowledgments from at least `W` of them. If `W` cannot be reached because of a partition, the write fails, preserving consistency.  
   **Follow‑up:** *What happens to the write if the partition heals later?*  
   **A:** Since the write never committed, the client must retry; no partial state is stored.

3. **Q:** *Describe hinted handoff in an AP system like Cassandra.*  
   **A:** When a replica is unreachable, the node that receives the write stores a *hint* indicating the missing replica. Once the partition resolves, the node forwards the hinted updates, allowing the cluster to converge.  
   **Follow‑up:** *How does Cassandra resolve conflicting writes after convergence?*  
   **A:** It uses timestamps (last‑write‑wins) or, if enabled, client‑supplied vector clocks for more precise conflict resolution.

4. **Q:** *Give an example where eventual consistency is acceptable.*  
   **A:** A news‑feed where a user may see a post a few seconds later is fine; the system prefers to stay online rather than block the request.  
   **Follow‑up:** *What risk does eventual consistency pose for such a feed?*  
   **A:** A user might briefly see an outdated count of likes or comments, but the inconsistency resolves quickly.

5. **Q:** *Why might a CP system still need conflict resolution?*  
   **A:** Even though reads are consistent, concurrent writes to different replicas during a partition can create divergent versions. CP systems must merge them (e.g., using timestamps) once the partition heals.  
   **Follow‑up:** *How does this differ from AP conflict handling?*  
   **A:** AP systems expect such conflicts more often and therefore provide built‑in mechanisms (vector clocks, read‑repair) to reconcile them automatically.

---

## Common Misconceptions  

| Misconception | Reality |
|---------------|---------|
| **“CP systems never have conflicts.”** | CP guarantees no stale reads, but concurrent writes during a partition can still conflict and need resolution. |
| **“AP systems always accept writes on any node.”** | Many AP stores require a write quorum or durability acknowledgments; they may still reject writes that cannot be persisted locally. |
| **“A database can be both CP and AP depending on network health.”** | The CAP trade‑off applies only during a partition; a system cannot simultaneously provide both guarantees. |
| **“Eventual consistency means data may never become consistent.”** | Eventual consistency guarantees convergence given no further updates; the delay is typically milliseconds to seconds. |
| **“All NoSQL databases are AP.”** | NoSQL includes both CP (e.g., HBase, MongoDB with strong write concern) and AP (e.g., Cassandra, DynamoDB) systems. |

<!-- END -->
