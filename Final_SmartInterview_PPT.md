# SmartInterview: Personalized Technical Interview Preparation in Higher Education

## Slide 1: Title Slide
**Project Name:** SmartInterview — Personalized Technical Interview Preparation in Higher Education  
**Project Team ID:** Team G-1392  
**Team Members:**  
- Shamakura Saiteja Goud (24BD1A665K)  
- Thodsam Srujan (24BD1A665R)  
- Vasireddy Vignesh Reddy (24BD1A665X)  
- Aelugu Ranith Kumar (25BD5A6615)  
- Konduri Abhiram (25BD5A6620)  

**Mentors:** Dr. TVG Sridevi  
**Department:** Computer Science and Engineering (AI & ML)  
**Institution:** Keshav Memorial Institute of Technology (KMIT)  
**Category:** Edu-Tech  

---

## Slide 2: Introduction & Problem Statement
**The Challenge in Modern Recruitment:**
- Engineering students face a stark disconnect between university curricula and dynamic industry job descriptions.
- Traditional preparation methods (static question banks, mock peers) fail to measure cognitive depth or adapt to the candidate's skill level.
- Existing literature reflects critical gaps:
  * **Base Paper 1 (Nagarajan et al., Feb 2026):** Built for enterprise recruiter filtering; lacks student learning roadmaps, code sandboxes, or curriculum grounding.
  * **Base Paper 2 (Wahid et al., March 2026):** Voice is strictly one-way (silent AI, candidate reads questions); rigid domain dropdowns without custom JD matching.
- **The Gap:** Candidates lack a low-latency, two-way conversational coach grounded in verified technical knowledge with objective evaluation.

---

## Slide 3: Proposed Solution — SmartInterview
**An AI-Powered, Adaptive Mock Interview Platform for Higher Education:**
- **3 Operational Modes:**
  1. *Job-Specific Mode:* Set-theoretic resume-to-JD mapping (Group A Overlap vs. Group B Gaps).
  2. *Topic-Based Mode:* Granular technical drilling across chosen CS domains.
  3. *Semester Syllabus Mode:* Isolated vector collections from university syllabus PDFs.
- **RAG-Grounded:** Retrieves from 402 curated CS chunks (Hit@1: 96.97%, Hit@3: 100%, MRR: 0.9798) to kill hallucinations.
- **Deterministic Cognitive Scaffolding:** State-driven difficulty scaling via Bloom's Revised Taxonomy.
- **Multi-Signal Evaluation:** 5-factor mathematical rubric eliminating subjective LLM "vibe grading".

---

## Slide 4: System Architecture
**Decoupled 4-Tier Distributed Technology Stack:**
- **Presentation Tier:** React 18 SPA (Vite, Tailwind CSS, Web Speech API audio visualizer).
- **Application Tier:** FastAPI (Python 3.10+, Uvicorn ASGI, Pydantic v2, HS256 JWT auth).
- **Core Intelligence Tier:**
  * ChromaDB HNSW vector store (`technical_kb`, 402 chunks, 384-dim S-BERT embeddings).
  * Groq Cloud LPU high-speed inference (`llama-3.3-70b-versatile` / `gpt-oss-120b`, 320ms TTFT).
  * Deterministic Python Bloom Adaptive Engine.
- **Voice Subsystem & Persistence:**
  * Microsoft Edge-TTS (`en-US-ChristopherNeural`, in-memory `io.BytesIO`, <= 1.2s latency).
  * Whisper Large-v3 STT with domain-primed technical vocabulary prompt.
  * MySQL 8.0 relational database for users, sessions, and transcripts.

---

## Slide 5: Core Workflow & Context Ingestion
**How SmartInterview personalizes the experience:**
1. **Document Ingestion:** Candidate uploads Resume (PDF) and target Job Description (or Syllabus).
2. **Deterministic Extraction:** PyMuPDF isolates technical skills and experience entities.
3. **Set-Theoretic Skill Gap Analysis:**
   - **Group A (Role Overlap):** Skills present in both Resume and JD -> Tested for verification.
   - **Group B (Role Gaps):** Skills required by JD but missing in Resume -> Tested for adaptability.
4. **Targeted Staging:** The interview dynamically focuses on validating Group A and bridging Group B.

---

## Slide 6: RAG-Grounded Question Generation
**Eliminating LLM Hallucinations at the Root:**
- **The Problem:** Zero-shot LLMs invent non-existent APIs, libraries, or flawed algorithmic complexities.
- **Our Curated Knowledge Base:** 402 verified computer science chunks across 50 concepts in 8 core domains (`dsa`, `dbms`, `os`, `cn`, `system-design`, `oop`, `design-patterns`, `ml-dl`).
- **Empirical Retrieval Benchmarks (33 Technical Domain Queries):**
  * **Hit@1 = 96.97%** (Top retrieved chunk is the exact ground truth).
  * **Hit@3 = 100.00%** (Correct technical answer key guaranteed in Top 3).
  * **Mean Reciprocal Rank (MRR) = 0.9798** (Near-perfect ranking precision).
  * **Retrieval Latency = 24.6 ms** (Well under 100ms threshold).
- **Generation:** Prompt is strictly bounded by retrieved reference chunks, making hallucination mathematically negligible.

---

## Slide 7: Deterministic Adaptive Progression (Bloom's Taxonomy)
**Strict Cognitive Difficulty Scaling:**
- Arbitrary LLM difficulty jumps replaced with a deterministic Python state machine mapped to **Bloom’s Revised Taxonomy** (*Remember, Understand, Apply, Analyze, Evaluate, Create*).
- **The State Transition Logic:**
  - **Score >= 80% (Mastery):** Advance to higher Bloom cognitive level (+1) or advance difficulty tier.
  - **Score 50% – 79% (Adequate):** Maintain current Bloom level and difficulty tier.
  - **Score < 50% (Remediation):** Regress Bloom level (-1) or lower difficulty to rebuild foundations.
- **Weakness-Biased Skill Selection:** Engine automatically prioritizes candidate's lowest-scoring skills.

---

## Slide 8: Multi-Signal Answer Evaluation
**Objective, Multi-Dimensional Scoring (Replacing "Vibe Grading"):**
- Evaluates candidate answers using a strict 5-part weighted mathematical formula:
  * **30% Technical Correctness:** Deep LLM logical reasoning and accuracy analysis.
  * **20% Completeness:** Coverage of all question constraints and edge cases.
  * **20% Relevance:** Focus, conciseness, and absence of filler rhetoric.
  * **15% Semantic Cosine Similarity:** S-BERT (`all-MiniLM-L6-v2`) matching candidate answer against verified ground-truth chunk.
  * **15% Concept Coverage:** Deterministic detection of mandatory technical keywords and concepts.
- **Why?** Blends semantic understanding with hard concept verification, ensuring reproducible, unbiased marks.

---

## Slide 9: Voice Interaction & Final Reporting
**Creating an Authentic, Low-Latency Interview Environment:**
- **Full Two-Way Voice:** Candidates speak naturally (transcribed via Whisper-large-v3 with domain prompt) and hear questions spoken aloud (Edge-TTS).
- **Latency Benchmarks:**
  * Voice synthesis latency <= 1.2 seconds (In-memory `io.BytesIO` streaming, zero disk footprint).
  * Total end-to-end turn turnaround < 2.5 seconds (Groq LPU 320ms TTFT).
- **Performance Analytics & Reporting:**
  * Real-time React dashboard with 5-axis radar chart and Bloom level progression.
  * Auto-generates downloadable ReportLab PDF report containing full transcripts, skill heatmaps, and personalized upskilling roadmaps.

---

## Slide 10: System Verification & Test Matrix
**Comprehensive Boundary & Integration Validation:**
- Evaluated and verified across 7 formal test cases:
  * **TC-01 (Auth):** Duplicate registration rejected (HTTP 400) — *PASSED*
  * **TC-02 (Parsing):** Corrupt/invalid file upload rejected (HTTP 400) — *PASSED*
  * **TC-03 (RAG Retrieval):** Domain-filtered Top-3 chunks returned in 24.6ms — *PASSED*
  * **TC-04 (Adaptive Escalation):** Score >= 80% advances Bloom level (+1) — *PASSED*
  * **TC-05 (Adaptive Remediation):** Score < 50% regresses Bloom level (-1) — *PASSED*
  * **TC-06 (Neural Voice):** In-memory TTS byte stream generated in <= 1.2s — *PASSED*
  * **TC-07 (Rubric Determinism):** 5-factor mathematical formula convergence — *PASSED*

---

## Slide 11: Conclusion & Questions
**Conclusion:**
SmartInterview bridges the gap between theoretical higher education and dynamic industry hiring. By combining 402-chunk RAG grounding (96.97% Hit@1), deterministic Bloom's taxonomy cognitive scaffolding, and multi-signal objective evaluation, we deliver an authentic, unbiased, low-latency interview preparation ecosystem.

**Thank You! We are now open for questions from the panel.**
