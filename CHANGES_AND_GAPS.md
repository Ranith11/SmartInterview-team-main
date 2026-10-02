# Changes and Gaps

### Changes Made vs Old Drafts
- Updated Department Name in the SRS to "Computer Science and Engineering (AI & ML)".
- Rewrote the PPT draft to follow a standard, professional 11-slide presentation format rather than a 5-member team speaking script, aligning better with standard academic defense expectations.

### Verification Gaps (Pending Runtime Audit)
The following elements require the project to be fully installed, booted, and benchmarked (Phase 1 Execution) to verify mathematically:
- **Retrieval Latency:** Target is <= 100ms. Needs runtime testing.
- **LLM Latency:** Target is <= 2.5s. Needs runtime testing.
- **TTS Latency:** Target is <= 1.2s. Needs runtime testing.
- **Exact Vector Count:** Documentation claims 402 chunks in ChromaDB. Needs live database query to confirm.

### Remaining Team Input Needed
- Confirm if you want me to execute the full Phase 1 runtime audit (booting the database, installing dependencies, and running 10x latency benchmarks).
- Confirm if the Markdown (.md) formats provided for the SRS and PPT are sufficient, as automated generation of perfectly formatted `.docx` and `.pptx` files is constrained by text-based AI limits.
