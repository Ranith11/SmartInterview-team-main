---
topic: Virtual Memory and Demand Paging
domain: os
subtopics: ["page fault handling", "copy-on-write"]
sources:
  - title: "Wikipedia: Memory paging"
    url: https://en.wikipedia.org/wiki/Memory_paging
    license: CC BY-SA 4.0
status: AUTO_VERIFIED
open_issues: 0
generator: openai/gpt-oss-120b
critic: openai/gpt-oss-20b
last_verified: 2026-10-02
human_reviewed: false
---
## Definition  

Virtual memory is a memory‑management technique that gives each process the illusion of a large, contiguous address space while the physical RAM may be much smaller.  The operating system (OS) keeps most pages of a process on secondary storage (disk) and brings them into RAM only when needed.  Demand paging is the core policy: a page is fetched from disk **only** after the process tries to access it.  Two mechanisms that make demand paging practical are **page‑fault handling** and **copy‑on‑write (COW)**.  Page‑fault handling describes what the OS does when a reference misses in RAM; COW lets multiple processes share a read‑only page and allocate a private copy only when one of them writes to it.

---

## How It Works  

### Page Fault Handling  

1. **Fault detection** – The CPU’s Memory Management Unit (MMU) translates a virtual address to a physical frame using the process’s page table.  If the entry is marked “not present”, the hardware raises a page‑fault exception and transfers control to the OS kernel.  

2. **Classify the fault** – The kernel checks whether the fault is *valid* (the page belongs to the process) or *invalid* (e.g., illegal address → segmentation fault).  

3. **Find a free frame** –  
   * If the free‑page queue contains an unused frame, the OS takes it.  
   * If no free frame exists, the OS selects a victim frame using a page‑replacement algorithm (LRU, clock, etc.).  
   * If the victim is *dirty* (modified since it was read), the OS writes it back to the swap area before reuse.  

4. **Load the page** –  
   * For a *demand‑paged* page that already exists on disk, the OS reads the appropriate block (the page) from the swap file or memory‑mapped file into the chosen frame.  
   * For a *zero‑filled* page (e.g., newly allocated heap), the OS may simply clear the frame to avoid leaking data.  

5. **Update the page table** – The entry for the faulting virtual page is filled with the physical frame number and marked present (and possibly read‑only or read‑write).  

6. **Resume the process** – The CPU restarts the instruction that caused the fault; from the program’s point of view the access succeeded transparently.  

**Worked example** –  
A 4 KB page‑size system runs Process A, which accesses virtual address `0x0040_1234`. The page table shows entry 0x0040 (page number) as “not present”. The MMU raises a fault. The OS finds a free frame `F7`, reads page 0x0040 from `swap.bin` into `F7`, updates the entry to point to `F7`, marks it present, and restarts the instruction. The access now completes in a few CPU cycles.

### Copy‑On‑Write (COW)  

COW is a lazy‑allocation optimization used when multiple processes need the same read‑only data (e.g., code pages or shared libraries).  

1. **Initial sharing** – When a process is created (fork) or when a library is mapped, the OS maps the same physical frame into the virtual address spaces of all participants and marks the page **read‑only** in every page table.  

2. **Write attempt** – If any process tries to write to the shared page, the MMU again raises a page‑fault because the page is read‑only.  

3. **COW handling** – The kernel allocates a fresh free frame, copies the contents of the shared page into it, updates the faulting process’s page‑table entry to point to the new frame with write permission, and clears the read‑only flag.  

4. **Other processes continue sharing** – The original frame remains unchanged and continues to be shared by the other processes.  

**Worked example** –  
Process B and Process C both map `/usr/lib/libX.so` at virtual address `0x7fff_8000`. The OS maps the same physical frame `F3` into both address spaces and sets the page‑table entries to read‑only. Process B later executes `*ptr = 42;` where `ptr` points into the library’s data segment. The MMU faults, the kernel copies `F3` to a new frame `F9`, updates B’s entry to point to `F9` with write permission, and resumes B. C still sees the original contents via `F3`.  

---

## Key Properties  

| Property | Page Fault Handling | Copy‑On‑Write |
|----------|--------------------|---------------|
| **Latency source** | Disk I/O (swap read/write) dominates the first fault for a page. | Only a memory copy; no disk I/O unless the page itself is swapped out. |
| **Memory overhead** | Requires a free frame for each faulted‑in page. | Adds one extra frame only when a write occurs; otherwise many processes share a single frame. |
| **Transparency** | The program never sees the fault; execution resumes automatically. | The program sees the same virtual address; the OS silently replaces the backing frame on first write. |
| **Typical use case** | Loading code/data on demand, handling stack growth, swapping out idle pages. | Forking processes, shared libraries, inter‑process communication via shared memory. |
| **Impact on paging** | Increases page‑fault rate if the working set exceeds RAM (possible thrashing). | Reduces page‑fault rate for reads because shared pages are already resident. |

---

## Real‑World Use  

* **Operating systems** – Linux, Windows, macOS all implement demand paging with page‑fault handlers written in kernel C.  The Linux kernel’s `do_page_fault()` routine follows the steps described above, invoking the page‑replacement subsystem when needed.  
* **Fork semantics** – Unix‑like OSes use COW for `fork()`.  The child’s address space initially points to the parent’s pages; only when either process writes does the kernel allocate a private copy.  This makes `fork()` cheap even for large processes.  
* **Shared libraries** – Dynamic linkers map `.so`/`.dll` files as read‑only pages.  Multiple programs run the same library code from a single physical copy, relying on COW to handle any rare writes (e.g., self‑modifying code).  
* **Containers & VMs** – Hypervisors use demand paging to back guest physical memory with host pages, and COW to implement copy‑on‑write snapshots for fast VM cloning.  

---

## Comparison  

| Aspect | Pure Demand Paging (no COW) | Demand Paging + COW |
|--------|----------------------------|---------------------|
| **Memory consumption** | Each process gets its own copy of every page it touches, even if the page is read‑only. | Read‑only pages are shared until a write forces a copy, dramatically reducing RAM use for many identical processes. |
| **Page‑fault frequency** | Higher for reads of shared code because each process must fault in its own copy. | Lower for reads; only the first process incurs the fault, others map the same frame instantly. |
| **Write‑fault cost** | Simple write to an already‑owned frame (no extra copy). | First write incurs an extra copy, adding a memory‑copy fault overhead. |
| **Implementation complexity** | Simpler page‑fault handler; no need to track shared‑read‑only status. | Requires reference‑counting of shared frames and handling of read‑only faults. |
| **Typical scenario** | Embedded systems with a single process or where memory is abundant. | General‑purpose OSes, servers running many similar processes, virtualization platforms. |

---

## Tradeoffs / When NOT to Use  

* **High write‑intensity workloads** – If a program frequently writes to pages that would otherwise be shared, COW’s copy cost can outweigh its memory‑saving benefit. In such cases, pre‑allocating private pages may be faster.  
* **Real‑time constraints** – Page‑fault handling involves disk I/O, which is nondeterministic. Systems with hard real‑time deadlines often disable demand paging or lock critical code/data in RAM.  
* **Limited disk bandwidth** – Heavy swapping can saturate I/O, leading to thrashing. In low‑I/O environments (e.g., embedded flash), designers may prefer static allocation over demand paging.  
* **Security‑sensitive contexts** – Sharing pages across security domains can leak timing information; some hardened kernels disable COW for certain privileged pages.  

---

## Interview Q&A  

1. **Q:** *What triggers a page fault and what are the OS’s first three actions?*  
   **A:** A page fault occurs when the MMU finds a “not present” entry for a virtual page. The OS first (1) validates the fault (is the address legal?), (2) obtains a free physical frame (or selects a victim), and (3) loads the required page from swap or zero‑fills the frame.  
   **Follow‑up:** *How does the OS decide which victim frame to evict?* – Typically via a page‑replacement algorithm such as LRU, clock, or working‑set based heuristics.

2. **Q:** *Explain copy‑on‑write and why it is useful after a `fork()`.*  
   **A:** After `fork()`, parent and child share all pages marked read‑only. When either writes, the fault handler copies the shared page to a new frame and updates only the writer’s page table. This avoids duplicating the entire address space, making `fork()` O(1) in time and memory.  
   **Follow‑up:** *What would happen if the OS didn’t use COW for `fork()`?* – It would have to copy every page immediately, incurring large memory and CPU overhead, especially for processes with many pages.

3. **Q:** *What is the difference between a “clean” and a “dirty” page in the context of page replacement?*  
   **A:** A clean page’s contents on disk match the version in RAM (e.g., code pages). A dirty page has been modified; before eviction it must be written back to swap to avoid data loss.  
   **Follow‑up:** *How does pre‑cleaning affect page‑fault latency?* – By writing dirty pages to disk proactively, the OS can obtain a free clean frame quickly, reducing the time spent during a fault.

4. **Q:** *Describe a scenario that leads to thrashing and one mitigation technique.*  
   **A:** Thrashing occurs when the combined working sets of running processes exceed physical memory, causing constant page faults (e.g., many large database queries). Mitigation: reduce concurrency, increase RAM, or adjust the page‑replacement algorithm to keep the most frequently used pages resident.  
   **Follow‑up:** *Why does “working‑set” size matter for thrashing?* – If each process’s working set fits in RAM, page faults are rare; once it exceeds RAM, each reference may fault, leading to thrashing.

5. **Q:** *How does the OS ensure that a newly allocated page does not leak data from a previous process?*  
   **A:** Before handing a free frame to a new process, the kernel clears (zeroes) the frame or fills it with a known pattern. This prevents residual data from being visible to the new owner.  
   **Follow‑up:** *Is zero‑filling required for COW pages?* – Yes, when a COW copy is created the new frame must be a fresh copy of the original data; any leftover bits would corrupt the program’s view.

---

## Common Misconceptions  

* **“Page faults are always bad.”** – A page fault is the mechanism that enables demand paging; the first fault for a needed page is expected and unavoidable. Performance problems arise only when faults become excessive (thrashing).  
* **“Copy‑on‑write copies the whole address space.”** – COW copies **only the page that is written**, leaving the rest of the address space shared. This is why `fork()` is cheap.  
* **“If a page is in RAM, it never goes to disk.”** – The OS may evict any clean or dirty page at any time to satisfy other demands; presence in RAM is not permanent.  
* **“All page‑fault handling is done in user space.”** – Page‑fault handling is a privileged kernel operation; user code never runs until the fault is resolved.  
* **“Demand paging eliminates the need for swap space.”** – Swap (or a paging file) is required to store pages that cannot fit in RAM; without it, the system would run out of memory as soon as the working set exceeds physical RAM.

<!-- END -->
