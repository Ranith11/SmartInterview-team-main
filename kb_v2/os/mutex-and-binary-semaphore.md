---
topic: Mutex and Binary Semaphore
domain: os
subtopics: ["differences", "deadlock potential", "priority inversion"]
sources:
  - title: "Wikipedia: Semaphore (programming)"
    url: https://en.wikipedia.org/wiki/Semaphore_(programming)
    license: CC BY-SA 4.0
status: NEEDS_HUMAN
open_issues: 3
generator: openai/gpt-oss-120b
critic: openai/gpt-oss-20b
last_verified: 2026-10-02
human_reviewed: false
---
## Definition  

A **mutex** (mutual exclusion lock) and a **binary semaphore** are synchronization primitives that allow only one thread to hold a resource at a time. Both can be in one of two states – *available* (value = 1) or *taken* (value = 0) – and both provide two operations:  

* **lock / acquire** (often called **wait** or **P**) – attempts to take the resource; if it is already taken the calling thread blocks.  
* **unlock / release** (often called **signal** or **V**) – returns the resource to the pool and wakes one waiting thread.  

The key difference lies in the *ownership* semantics and the intended usage pattern, which in turn affect deadlock potential and susceptibility to priority inversion.

---

## How It Works  

### 1. Differences  

| Aspect | Mutex | Binary Semaphore |
|--------|-------|-------------------|
| **Ownership** | The thread that successfully locks the mutex **must** be the one that unlocks it. | Any thread may signal a binary semaphore, regardless of which thread performed the previous wait. |
| **Blocking semantics** | Usually implements *strict* FIFO or priority‑ordered wait queues; many implementations guarantee that a blocked thread will eventually acquire the lock (no “spurious wake‑ups”). | May allow *signal* to wake a thread that never performed the matching *wait* (e.g., a semaphore initialized to 1 can be signaled even if no thread is waiting). |
| **Re‑entrancy** | Most mutexes are **non‑reentrant**; a thread that already holds the lock and tries to lock it again will deadlock (unless a *recursive* mutex is used). | Binary semaphores are not tied to a particular thread, so a thread can `wait` then `signal` repeatedly without deadlock, but this defeats the mutual‑exclusion purpose. |
| **Typical API** | `pthread_mutex_lock`, `pthread_mutex_unlock` (POSIX); `std::mutex::lock`, `unlock` (C++). | `sem_wait`, `sem_post` (POSIX); `java.util.concurrent.Semaphore.acquire`, `release`. |
| **Use case** | Protecting a critical section that must be accessed by **exactly one** thread at a time. | Simple “turnstile” where the resource does not need to remember *who* holds it (e.g., counting a single token). |

**Worked example (C‑like pseudocode)**  

```c
// Mutex example
pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;

void threadA() {
    pthread_mutex_lock(&m);   // acquire
    // critical section
    pthread_mutex_unlock(&m); // release
}

// Binary semaphore example
sem_t s;
sem_init(&s, 0, 1);           // initial value 1 (available)

void threadB() {
    sem_wait(&s);             // wait (decrements to 0)
    // critical section
    sem_post(&s);             // signal (increments to 1)
}
```

In the mutex case, only the thread that called `pthread_mutex_lock` may later call `pthread_mutex_unlock`. In the semaphore case, any thread could call `sem_post`, even one that never called `sem_wait`.

### 2. Deadlock Potential  

Deadlock occurs when a set of threads each wait for a resource held by another thread in the set, forming a cycle. Both mutexes and binary semaphores can be part of a deadlock, but the risk differs:

* **Mutexes** – Because ownership is enforced, a thread that already holds a mutex cannot acquire it again (unless it is a recursive mutex). This prevents *self‑deadlock* but does not eliminate classic deadlock involving multiple mutexes. Example: Thread 1 locks `A` then `B`; Thread 2 locks `B` then `A`. Both block forever.

* **Binary semaphores** – Since any thread may signal, a programmer might mistakenly signal a semaphore that no one is waiting on, or forget to signal after a wait, leaving the semaphore permanently at 0. Moreover, if a thread performs `wait` on two binary semaphores in opposite order from another thread, the same circular wait can arise.

**Worked deadlock scenario (mutex)**  

```c
pthread_mutex_t A = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t B = PTHREAD_MUTEX_INITIALIZER;

void *t1(void *) {
    pthread_mutex_lock(&A);
    sleep(1);                     // force interleaving
    pthread_mutex_lock(&B);      // blocks here
    // ...
    pthread_mutex_unlock(&B);
    pthread_mutex_unlock(&A);
}
void *t2(void *) {
    pthread_mutex_lock(&B);
    sleep(1);
    pthread_mutex_lock(&A);      // blocks here → deadlock
    // ...
}
```

**Worked deadlock scenario (binary semaphore)**  

```c
sem_t s1, s2;
sem_init(&s1, 0, 1);
sem_init(&s2, 0, 1);

void *t1(void *) {
    sem_wait(&s1);
    sleep(1);
    sem_wait(&s2);   // blocks
    // ...
    sem_post(&s2);
    sem_post(&s1);
}
void *t2(void *) {
    sem_wait(&s2);
    sleep(1);
    sem_wait(&s1);   // blocks → deadlock
}
```

Both patterns illustrate the classic “hold‑and‑wait” condition; the difference is that with a mutex the programmer is forced to remember which thread holds the lock, whereas a binary semaphore offers no such guarantee.

### 3. Priority Inversion  

Priority inversion happens when a high‑priority thread is blocked by a lower‑priority thread that holds a lock, while a medium‑priority thread runs freely.  

* **Mutexes** – Many OS kernels implement *priority inheritance* for mutexes: when a high‑priority thread blocks on a mutex held by a lower‑priority thread, the holder temporarily inherits the higher priority, preventing medium‑priority threads from pre‑empting it. This mitigates inversion.  

* **Binary semaphores** – Standard POSIX semaphores do **not** provide priority inheritance. If a high‑priority thread waits on a binary semaphore held by a low‑priority thread, a medium‑priority thread can continue to run, extending the blocking time.  

**Worked priority‑inversion example (mutex with inheritance)**  

```c
// Assume OS supports priority inheritance for pthread_mutex
pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;

void low() {
    pthread_mutex_lock(&m);   // runs at priority 10
    sleep(5);                 // holds lock while medium runs
    pthread_mutex_unlock(&m);
}
void medium() {
    // priority 20, does unrelated work
}
void high() {
    // priority 30
    pthread_mutex_lock(&m);   // blocks, OS boosts low's priority to 30
    // critical section
    pthread_mutex_unlock(&m);
}
```

When `high` blocks, the kernel raises `low`’s priority, allowing it to finish quickly and release the mutex, after which `high` proceeds.  

**Worked priority‑inversion example (binary semaphore, no inheritance)**  

```c
sem_t s;
sem_init(&s, 0, 1);   // initial token

void low() {
    sem_wait(&s);      // priority 10
    sleep(5);
    sem_post(&s);
}
void medium() {
    // priority 20, runs while low sleeps
}
void high() {
    // priority 30
    sem_wait(&s);      // blocks, but low stays at priority 10
    // critical section
    sem_post(&s);
}
```

Here, `medium` can pre‑empt `low`, extending the time `high` waits, because the semaphore does not trigger priority inheritance.

---

## Key Properties  

| Property | Mutex | Binary Semaphore |
|----------|-------|-------------------|
| **Strict ownership** | Yes – only owner may unlock. | No – any thread may signal. |
| **Recursive variant** | Available (recursive mutex) but not default. | Not applicable; recursion meaningless. |
| **Priority inheritance** | Often built‑in (POSIX, Windows). | Rarely provided. |
| **Spurious wake‑ups** | Generally none (implementation‑defined). | Possible if `post` occurs without a waiting thread. |
| **Fairness** | Queue can be FIFO or priority‑ordered. | Queue semantics similar, but signal may wake any waiting thread. |
| **Use for counting** | No – only binary. | Binary is a special case of counting semaphore (max = 1). |

---

## Real‑World Use  

* **Mutex** – Protecting shared data structures (hash tables, file descriptors), implementing critical sections in kernel drivers, synchronizing access to hardware registers.  
* **Binary Semaphore** – Implementing simple “resource available” flags (e.g., a single printer token), coordinating start‑up/shutdown sequences where the signaling thread is not the same as the waiting thread, or as a lightweight alternative when ownership tracking is unnecessary.

---

## Comparison  

| Criterion | Mutex | Binary Semaphore |
|-----------|-------|-------------------|
| **Safety** (preventing accidental release) | High – only owner can release. | Lower – accidental `post` can make the resource appear free. |
| **Flexibility** | Less flexible (ownership enforced). | More flexible (any thread can signal). |
| **Performance** | Slightly higher overhead due to ownership checks and possible priority‑inheritance bookkeeping. | Typically marginally cheaper, but modern kernels make the difference negligible. |
| **Deadlock avoidance** | Easier to reason about because of ownership; many static analysis tools target mutex misuse. | Harder; misuse of `post` can mask deadlocks. |
| **Priority inversion handling** | Built‑in in many OSes. | Usually absent. |

---

## Tradeoffs / When NOT to Use  

* **Do not use a mutex** when you need a thread‑agnostic “event” that can be signaled by any producer and waited on by any consumer (e.g., a one‑shot barrier). A binary semaphore or condition variable is more appropriate.  
* **Do not use a binary semaphore** as a drop‑in replacement for a mutex in code that relies on ownership semantics, because accidental `post` by the wrong thread can corrupt the critical section’s protection.  
* Avoid binary semaphores in real‑time systems where priority inversion is a concern unless the platform explicitly provides priority inheritance for semaphores.  
* If you need recursive locking, prefer a recursive mutex rather than trying to emulate recursion with a binary semaphore (which would require extra bookkeeping and is error‑prone).

---

## Interview Q&A  

1. **Q:** *What is the main semantic difference between a mutex and a binary semaphore?*  
   **A:** A mutex enforces ownership – the thread that locks it must be the one that unlocks it. A binary semaphore does not track ownership; any thread may signal it regardless of who performed the previous wait.  
   **Follow‑up:** *Why does this matter for correctness?*  

2. **Q:** *Can a binary semaphore cause a deadlock that a mutex would not?*  
   **A:** Yes. Because any thread can signal, a programmer may forget to signal after a wait, leaving the semaphore at 0 and blocking all future waiters. A mutex would block only if the owning thread never unlocks, which is usually easier to detect.  
   **Follow‑up:** *Show a code snippet that deadlocks with a binary semaphore but not with a mutex.*  

3. **Q:** *Explain priority inversion and how mutexes mitigate it.*  
   **A:** Priority inversion occurs when a high‑priority thread waits for a lock held by a low‑priority thread while a medium‑priority thread runs. Many OSes implement priority inheritance for mutexes: the low‑priority holder temporarily inherits the high priority, preventing pre‑emption by medium‑priority threads. Binary semaphores typically lack this feature.  
   **Follow‑up:** *What would happen if the same scenario used a binary semaphore?*  

4. **Q:** *When would you deliberately choose a binary semaphore over a mutex?*  
   **A:** When the synchronization pattern does not require ownership, such as signaling an event from one thread to another, implementing a simple token bucket, or coordinating start‑up where the signaling thread is different from the waiting thread.  
   **Follow‑up:** *Give an example of a producer–consumer queue that uses a binary semaphore.*  

5. **Q:** *Is a recursive mutex the same as a binary semaphore?*  
   **A:** No. A recursive mutex allows the same thread to lock multiple times, keeping a count internally and requiring the same number of unlocks. A binary semaphore has no notion of which thread holds it; repeated waits by the same thread will block if the value is already 0.  
   **Follow‑up:** *What pitfalls arise if you misuse a binary semaphore to emulate recursion?*  

---

## Common Misconceptions  

1. **“A binary semaphore is just a mutex.”**  
   Candidates often claim interchangeability. The lack of ownership means a binary semaphore can be signaled by the wrong thread, breaking mutual exclusion guarantees.

2. **“Mutexes never cause deadlock.”**  
   While ownership reduces certain mistakes, classic deadlock patterns (circular wait on multiple mutexes) still apply.

3. **“Priority inversion only happens with semaphores.”**  
   It can happen with any lock; however, mutexes commonly have built‑in priority inheritance, whereas binary semaphores usually do not.

4. **“If I `post` a binary semaphore when no thread is waiting, nothing bad happens.”**  
   The semaphore’s value becomes 1, allowing the next `wait` to succeed without blocking. This can mask logic errors where a thread expected to wait but proceeds immediately.

5. **“Recursive mutexes are always safe.”**  
   Recursive locks can hide design flaws and increase the risk of unintentional lock retention, especially when combined with other non‑recursive locks.

<!-- END -->
