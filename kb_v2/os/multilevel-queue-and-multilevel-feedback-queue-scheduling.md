---
topic: Multilevel Queue and Multilevel Feedback Queue Scheduling
domain: os
subtopics: []
sources:
  - title: "Wikipedia: Multilevel feedback queue"
    url: https://en.wikipedia.org/wiki/Multilevel_feedback_queue
    license: CC BY-SA 4.0
status: NEEDS_HUMAN
open_issues: 3
generator: openai/gpt-oss-120b
critic: openai/gpt-oss-20b
last_verified: 2026-10-02
human_reviewed: false
---
## Definition  

**Multilevel Queue (MLQ) Scheduling** – A static priority‑based scheduler that partitions the ready‑process pool into several distinct FIFO (or other) queues. Each queue represents a class of processes (e.g., foreground, batch, system) and a process stays in the queue it was assigned to for its entire lifetime. The scheduler always selects a process from the highest‑priority non‑empty queue.  

**Multilevel Feedback Queue (MLFQ) Scheduling** – A dynamic extension of MLQ that allows processes to move between queues based on their observed CPU‑burst behavior. New processes start in the highest‑priority queue; if they consume their entire time quantum they are demoted to a lower‑priority queue, while processes that voluntarily relinquish the CPU (typically I/O‑bound or interactive) are promoted. The goal is to give short‑burst and interactive jobs rapid service while still guaranteeing progress for long‑running CPU‑bound jobs.  

Both schemes are pre‑emptive and aim to keep the CPU busy while providing a balance between responsiveness and throughput.

---

## How It Works  

### Multilevel Queue  

1. **Queue creation** – System administrator defines *k* queues, each with its own scheduling policy (commonly FIFO or round‑robin).  
2. **Process admission** – When a process is created, a classification function (e.g., based on user ID, process type, or explicit priority) assigns it to one of the queues.  
3. **Selection** – The dispatcher scans queues from highest to lowest priority; the first ready process it finds is dispatched.  
4. **Execution** – The selected queue’s policy determines the time slice (e.g., round‑robin quantum). When the quantum expires or the process blocks, control returns to the scheduler, which again starts from the top queue.  

**Worked example** – Suppose three queues:  

| Queue | Priority | Policy   |
|------|----------|----------|
| Q0   | 1 (high) | RR, q=20 ms |
| Q1   | 2        | FIFO |
| Q2   | 3 (low)  | FIFO |

Process A (interactive) → Q0, Process B (batch) → Q1, Process C (background) → Q2.  

- Scheduler picks A from Q0, runs 20 ms, then A blocks for I/O.  
- Scheduler again starts at Q0; Q0 is empty, so it picks B from Q1, runs to completion (FIFO).  
- After B finishes, scheduler picks C from Q2.  

### Multilevel Feedback Queue  

1. **Initialize** – Create *k* queues, each with an increasing time quantum (e.g., q₀ = 8 ms, q₁ = 16 ms, q₂ = 32 ms).  
2. **New process** – Insert at the tail of the top‑level queue Q₀.  
3. **Dispatch** – Always choose the head of the highest‑priority non‑empty queue.  
4. **Quantum expiration** –  
   * If the process finishes before its quantum, it exits.  
   * If it yields (e.g., performs I/O) before the quantum expires, it stays in the same queue (or may be promoted one level).  
   * If it uses the entire quantum, pre‑empt it and enqueue it at the tail of the next lower queue.  
5. **Aging** – Periodically promote processes that have waited too long in low queues to prevent starvation.  

**Worked example** – Three queues with quanta 8 ms, 16 ms, 32 ms.

| Process | CPU bursts (ms) | Behavior |
|---------|----------------|----------|
| P1      | 5, 3, 4        | Short, yields after each burst (I/O) |
| P2      | 20, 20         | Long CPU‑bound |
| P3      | 6, 2, 10       | Mixed |

Step‑by‑step:  

1. All three enter Q₀. Scheduler runs P1 for 5 ms → finishes burst, blocks for I/O → re‑enters Q₀ tail.  
2. Next head is P2; quantum is 8 ms, but P2 needs 20 ms, so after 8 ms it is pre‑empted and moved to Q₁ tail.  
3. Scheduler now runs P3 for 6 ms (finishes burst, blocks) → re‑enters Q₀.  
4. Q₀ now has P1 and P3 (both waiting for I/O). Scheduler picks the next ready process from Q₁: P2 runs another 8 ms, demoted to Q₂.  
5. When I/O completes, P1 returns to Q₀ and finishes its remaining 3 ms quickly, then its 4 ms burst, exiting the system.  

The algorithm automatically pushes CPU‑bound P2 down to lower‑priority queues while keeping interactive P1 near the top.

---

## Complexity  

*Insertion* and *removal* from any FIFO queue are O(1).  
*Queue selection* requires scanning at most *k* queues, so the worst‑case dispatch decision is O(k). In practice *k* is a small constant (often ≤ 5), making the overhead negligible.

---

## Key Properties  

| Property                     | MLQ                              | MLFQ                              |
|------------------------------|----------------------------------|-----------------------------------|
| **Static vs. dynamic**       | Static assignment                | Dynamic promotion/demotion       |
| **Responsiveness**           | Depends on priority assignment   | High for short/interactive jobs  |
| **Starvation protection**    | Requires explicit aging policy   | Built‑in aging + optional aging  |
| **Throughput**               | May suffer if high‑priority queues are overloaded | Balances throughput by eventually giving CPU to long jobs |
| **Implementation cost**      | Simple (fixed queues)            | Slightly more complex (track quanta, promotions) |
| **Fairness**                 | Priority‑driven, can be unfair  | More equitable over time         |

---

## Real‑World Use  

* **Multilevel Queue** – Early UNIX kernels used separate queues for system, interactive, and batch processes. Modern real‑time operating systems (e.g., VxWorks) still expose static priority queues for hard‑real‑time tasks.  
* **Multilevel Feedback Queue** – The classic MLFQ appears in many teaching OS kernels (e.g., the xv6 scheduler exercise) and influenced the design of the Linux Completely Fair Scheduler’s “nice” levels, which approximate feedback behavior by adjusting virtual runtimes. Solaris 2.6 employed an MLFQ‑style time‑sharing scheduler.  

---

## Comparison  

| Aspect                | Multilevel Queue                              | Multilevel Feedback Queue                     |
|-----------------------|-----------------------------------------------|----------------------------------------------|
| **Process movement** | Never moves after admission                  | Moves up/down based on CPU usage and I/O     |
| **Configuration**    | Fixed number of queues, fixed policies       | Requires additional parameters: quanta per level, promotion/demotion rules |
| **Adaptivity**        | Low – static priorities only                 | High – reacts to runtime behavior           |
| **Typical use case** | Systems with well‑defined job classes (e.g., real‑time vs. batch) | General‑purpose OS where workload mix is unpredictable |

---

## Tradeoffs / When NOT to Use  

*Use MLQ when* you have clearly separated workloads with strict priority guarantees (e.g., safety‑critical tasks). Avoid it if workloads are heterogeneous; static assignment can cause high‑priority queues to become bottlenecks, starving lower‑priority jobs.  

*Use MLFQ when* you need a single scheduler that automatically adapts to interactive vs. CPU‑bound processes. However, MLFQ can be overkill for embedded systems with limited resources, and its parameters (number of levels, quantum sizes) must be tuned; poor choices may lead to excessive context switches or insufficient responsiveness.  

Do **not** use MLFQ in hard real‑time environments where deterministic worst‑case response times are required, because the dynamic demotion can unpredictably increase latency.

---

## Interview Q&A  

1. **Q:** *What is the main difference between Multilevel Queue and Multilevel Feedback Queue scheduling?*  
   **A:** MLQ assigns each process to a fixed priority queue for its entire lifetime, while MLFQ allows processes to move between queues based on their observed CPU‑burst behavior, promoting interactive jobs and demoting CPU‑bound jobs.  
   **Follow‑up:** *How does MLFQ prevent starvation of low‑priority processes?*  
   **A:** By aging—periodically promoting processes that have waited too long—or by eventually allowing them to run in the lowest‑level round‑robin queue.

2. **Q:** *Explain how a process is demoted in an MLFQ scheduler.*  
   **A:** If a process consumes its entire time quantum at a given level, the scheduler pre‑empts it and enqueues it at the tail of the next lower‑priority queue, which has a larger quantum.  
   **Follow‑up:** *What happens if the process yields before the quantum expires?*  
   **A:** It either stays in the same queue or may be promoted one level, depending on the implementation’s promotion rule.

3. **Q:** *Why does MLFQ use increasing time quanta for lower queues?*  
   **A:** Larger quanta reduce context‑switch overhead for CPU‑bound jobs that have already proven they need more CPU time, while still giving short‑burst jobs frequent chances to run in higher queues.  
   **Follow‑up:** *What would be the effect of using the same quantum for all levels?*  
   **A:** The scheduler would behave like a simple round‑robin across all processes, losing the benefit of prioritizing short/interactive jobs.

4. **Q:** *How would you implement aging in an MLQ system?*  
   **A:** Periodically scan lower‑priority queues; if a process has waited longer than a threshold, move it to a higher‑priority queue. This can be done with a timer interrupt that triggers the promotion.  
   **Follow‑up:** *What is a potential downside of aggressive aging?*  
   **A:** It may undermine the intended priority hierarchy, allowing low‑priority jobs to pre‑empt higher‑priority interactive tasks.

5. **Q:** *In what scenarios is MLFQ unsuitable?*  
   **A:** Hard real‑time systems where worst‑case response time must be bounded, or extremely memory‑constrained embedded devices where the bookkeeping for multiple queues and quanta is too costly.  
   **Follow‑up:** *What alternative scheduler would you choose for hard real‑time tasks?*  
   **A:** A static priority pre‑emptive scheduler (e.g., Rate‑Monotonic or Earliest‑Deadline‑First) that guarantees deterministic latencies.

---

## Common Misconceptions  

* **“MLFQ always gives the shortest job first.”** – MLFQ approximates SJF by favoring jobs that voluntarily yield early, but it does not guarantee strict shortest‑job ordering.  
* **“A process can be promoted indefinitely.”** – Most implementations cap promotion at the highest queue; once there, the process stays unless it exhausts the quantum and is demoted again.  
* **“MLQ and MLFQ are the same because both have multiple queues.”** – The key distinction is *static* vs. *dynamic* placement; MLQ never moves a process after admission, whereas MLFQ does.  
* **“A larger number of queues always improves performance.”** – Adding more levels increases scheduler complexity and may cause unnecessary context switches without measurable benefit.  
* **“If a process blocks for I/O, it is automatically promoted.”** – Promotion on I/O is optional; some MLFQ designs only demote on quantum expiration and rely on aging for promotion.

<!-- END -->
