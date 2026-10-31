# SmartInterview: Personalized Technical Interview Preparation in Higher Education
**Grounding via Hybrid Graph RAG & Deterministic Bloom's Scaffolding**

---

## Slide 1: Title Slide
**Project Name:** SmartInterview — Personalized Technical Interview Preparation in Higher Education  
**Project Team ID:** Team G-1392  
**Team Members:**  
- Shamakura Saiteja Goud (24BD1A665K)  
- Thodsam Srujan (24BD1A665R)  
- Vasireddy Vignesh Reddy (24BD1A665X)  
- Aelugu Ranith Kumar (25BD5A6615)  
- Konduri Abhiram (25BD5A6620)  

**Faculty Guide & Mentor:** Dr. TVG Sridevi, Professor  
**Department:** Computer Science and Engineering (AI & ML)  
**Institution:** Keshav Memorial Institute of Technology (KMIT), Hyderabad  
**Affiliation:** Jawaharlal Nehru Technological University Hyderabad (JNTUH)  
**Category:** Edu-Tech / Applied Artificial Intelligence  

---

## Slide 2: Literature Gaps & Problem Statement
**The Challenge in Modern Technical Recruitment:**
- Engineering students face a severe disconnect between theoretical academic syllabi and fast-evolving industry Job Descriptions (JDs).
- High interview anxiety, lack of verbal articulation practice, and high campus recruitment attrition.
- Static coding portals (LeetCode, HackerRank) test binary syntax but cannot simulate architectural trade-off inquiries or verbal dialogues.

**Critical Gaps in Foundational 2026 Literature:**
- **Base Paper 1 (Nagarajan et al., Feb 2026 — IJMRR):**
  * Built strictly for enterprise recruiters as an exclusionary filter.
  * Lacks candidate feedback, diagnostic reports, code sandboxes, or curriculum grounding.
- **Base Paper 2 (Wahid et al., March 2026 — IJERT):**
  * Silent AI: voice is strictly one-way (Whisper STT only, candidate must read text questions).
  * Rigid domain dropdowns without custom JD matching.
- **The Core Gap:** Students lack a grounded, low-latency, two-way conversational coach with deterministic cognitive progression and objective multi-signal grading.

---

## Slide 3: Proposed Solution — SmartInterview
**An Adaptive, Grounded Mock Interview & Remediation Platform for Higher Education:**
- **3 Distinct Operational Modes:**
  1. *Job-Specific Mode:* Set-theoretic Resume-to-JD mapping (Group A Overlap vs. Group B Gaps).
  2. *Topic-Based Mode:* Granular technical drilling across 8 core Computer Science domains.
  3. *Semester Syllabus Mode:* Isolated vector collections generated dynamically from university syllabus PDFs.
- **Hybrid Graph RAG Grounding:** Combines Dense Semantic ChromaDB, BM25Okapi Lexical Search, and NetworkX Knowledge Graph Traversal to completely eliminate technical hallucinations.
- **Deterministic Cognitive Scaffolding:** State-driven difficulty scaling via Bloom's Revised Taxonomy (*Remember* through *Create*).
- **Objective Multi-Signal Evaluation:** 5-factor mathematical rubric eliminating subjective LLM "vibe grading".
- **Remedial Mastery Mode:** Automated weakness diagnosis, prerequisite ontology traversal, and 1-click focused retests.

---

## Slide 4: Decoupled 4-Tier Distributed System Architecture
**Visual Asset:** `SmartInterview_Deliverables/05_System_Diagrams/Architecture.png`

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. PRESENTATION TIER: React 18 SPA + Vite 6 + Tailwind CSS                  │
│    • Resume & JD Upload UI  • Skill Gap Matrix  • Canvas Audio Waveform     │
│    • Real-Time Interview Room  • 5-Axis Radar Chart Performance Dashboard   │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. APPLICATION TIER: FastAPI 0.115 ASGI + Python 3.10+ + Uvicorn            │
│    • PyMuPDF C-level parser  • Deterministic Bloom state machine            │
│    • 5-signal rubric evaluator  • In-memory neural voice streaming (BytesIO)│
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. PERSISTENCE & VECTOR TIER: MySQL 8.0 (InnoDB) + ChromaDB + NetworkX      │
│    • MySQL: Strict ACID transactions, 7 relational tables, JSON state column│
│    • ChromaDB: Local HNSW cosine vector index, 402 CS chunks, 0ms network   │
│    • NetworkX: In-memory prerequisite knowledge graph ontology              │
├─────────────────────────────────────────────────────────────────────────────┤
│ 4. INFERENCE & VOICE TIER: Groq Cloud LPU + Microsoft Edge-TTS              │
│    • Groq LPU: Llama-3.3-70B / GPT-OSS-120B (>500 t/s, 320ms TTFT)          │
│    • Edge-TTS: In-memory async chunked WebSocket audio streaming (<= 1.2s)  │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Points:**
- Enforces strict boundary between local zero-cost persistence and accelerated cloud inference.
- Operates smoothly on commodity laboratory hardware without requiring local GPUs.

---

## Slide 5: Core Workflow & Context Ingestion Pipeline
**Visual Asset:** `SmartInterview_Deliverables/05_System_Diagrams/Workflow.png`

**Personalized Technical Staging Pipeline:**
1. **Document Ingestion:** Candidate uploads Resume (PDF) and target Job Description (or Syllabus).
2. **Deterministic Extraction:** PyMuPDF isolates technical competencies, frameworks, and project details.
3. **Set-Theoretic Skill Gap Analysis:**
   - *Group A (Role Overlap):* Skills present in both Resume & JD -> Targeted for deep technical verification.
   - *Group B (Role Gaps):* Skills required by JD but missing in Resume -> Targeted for adaptability & breadth.
4. **Targeted Question Staging:** Generates contextual questions grounded in verified textbook reference chunks.
5. **Real-Time Dialogue & Multi-Signal Evaluation:** Transcribes candidate audio and scores performance across 5 mathematical signals.
6. **Bloom Cognitive Escalation / Remediation:** Advances or regresses cognitive levels dynamically based on mastery.

---

## Slide 6: Hybrid Graph RAG Architecture & Ontology
**Tri-Retrieval Engine with Reciprocal Rank Fusion (RRF):**
- **The Challenge:** Vanilla vector search misses exact technical keywords (`2PL`, `ACID`) and cannot traverse conceptual prerequisites.
- **Tri-Retrieval Pipeline:**
  1. *Dense Semantic Retrieval (ChromaDB + all-MiniLM-L6-v2):* 384-dimensional cosine index across 402 curated CS topic chunks in 8 domains.
  2. *Lexical Keyword Retrieval (BM25Okapi):* Deterministic exact token matching for symbols, algorithms, and acronyms.
  3. *Knowledge Graph Traversal (NetworkX In-Memory / Neo4j):* Directed graph mapping 50 CS concepts, prerequisite edges, and Bloom cognitive depths (`data/graph_data.json`).
- **Reciprocal Rank Fusion (RRF, $k=60$):**
  $$RRF(d) = \sum_{m \in M} \frac{1}{60 + r_m(d)}$$
- **Empirical Benchmark Results (33 Technical Domain Queries):**
  - **Hit@1 = 96.97%** (Top retrieved chunk is the exact ground-truth answer key).
  - **Hit@3 = 100.00%** (Correct reference chunk guaranteed in top 3).
  - **Mean Reciprocal Rank (MRR) = 0.9798** (Near-perfect ranking precision).
  - **Retrieval Latency = 24.6 ms** (Sub-100ms vector search via local ChromaDB HNSW).

---

## Slide 7: Relational Data Schema & Entity Architecture (ERD)
**Visual Asset:** `SmartInterview_Deliverables/05_System_Diagrams/ERD.png`

**Robust 7-Table Relational Schema (MySQL 8.0 InnoDB):**
- `users`: Candidate credentials, bcrypt password hash, timestamps.
- `resumes`: PyMuPDF parsed skills, work experience, projects JSON.
- `job_descriptions`: Target JD entities, domain skills, requirements JSON.
- `interview_sessions`: Session difficulty, question count, status, serialized `AdaptiveState` JSON, Bloom level.
- `interview_questions`: Question text, Bloom tier, skill, reference RAG chunk ID.
- `answers`: Candidate audio transcription and response text.
- `answer_evaluations`: Multi-signal 5-factor scores, feedback, strengths, weaknesses.
- **Guarantees:** Foreign keys with `ON DELETE CASCADE`, strict ACID transactions, and JSON state serialization preventing session loss.

---

## Slide 8: Deterministic Cognitive Scaffolding (Bloom's Taxonomy)
**Strict Cognitive Progression (Replacing Arbitrary LLM Difficulty):**
- Maps questions systematically across **Bloom’s Revised Taxonomy**:
  * *Remember (L1) -> Understand (L2) -> Apply (L3) -> Analyze (L4) -> Evaluate (L5) -> Create (L6)*.
- **Deterministic State Transition Logic:**
  - **Score $\ge$ 80% (Mastery):** Advance to higher Bloom level (+1) or advance difficulty tier (*Easy -> Medium -> Hard*).
  - **Score 50% – 79% (Adequate):** Maintain current Bloom level and difficulty tier for concept reinforcement.
  - **Score < 50% (Remediation):** Regress Bloom level (-1) or lower difficulty to rebuild core principles.
- **Boundary Protections:**
  - *Ceiling Protection:* At Create (L6) + Hard, scores maintain maximum cognitive depth.
  - *Floor Protection:* At Remember (L1) + Easy, floors cleanly without negative underflow.
- **Weakness-Biased Skill Selection Algorithm:** Automatically samples next questions from lowest-scoring skills to eliminate competency blind spots.

---

## Slide 9: Multi-Signal Answer Evaluation (Eliminating "Vibe Grading")
**Objective, Multi-Dimensional Scoring Rubric:**
- Evaluates candidate answers using a strict 5-part weighted mathematical formula:
  * **30% Technical Correctness:** Deep LLM logical reasoning and factual accuracy verified against retrieved ground truth.
  * **20% Completeness:** Coverage of all question constraints, trade-offs, and edge cases.
  * **20% Relevance:** Focus, conciseness, and absence of conversational filler rhetoric.
  * **15% Semantic Cosine Similarity:** Sentence-BERT (`all-MiniLM-L6-v2`) matching candidate answer against verified ground-truth chunk.
  * **15% Explicit Concept Coverage:** Deterministic keyword and entity regex detection for mandatory technical terms.
- **Why This Split?** Blends semantic understanding with hard concept verification, ensuring reproducible, unbiased scoring immune to prompt drift.

---

## Slide 10: Live Spoken Interview Room & Neural Voice
**Visual Asset:** `screenshots/13_live_interview_session.png`

**Real-Time Two-Way Conversational Dialogue:**
- **Text-to-Speech (Microsoft Edge-TTS):**
  * Professional `en-US-ChristopherNeural` technical recruiter voice profile.
  * Synthesized directly into in-memory `io.BytesIO` buffers (latency $\le 1.2\text{s}$, zero disk footprint).
- **Speech-to-Text (Groq Whisper Large-v3):**
  * High-accuracy neural speech transcription conditioned on CS domain vocabulary priming.
- **Interactive Visual Interface:**
  * Displays active Bloom taxonomy level badge (e.g. `Analyze` Level 4).
  * Real-time speech recognition status, waveform audio controls, and fallback text area.
  * Sub-2.5s end-to-end turnaround eliminates awkward conversational pauses.

---

## Slide 11: Candidate Evaluation Scorecard & Analytics
**Visual Asset:** `screenshots/11_results_scorecard.png`

**Multi-Dimensional Candidate Feedback:**
- **Overall Session Score & Performance Tier:** Percentage score with Bloom cognitive depth indicators.
- **5-Axis Radar Breakdown Chart:** Visualizes Correctness, Completeness, Relevance, Semantic Similarity, and Concept Coverage.
- **Granular Question Transcripts:** Side-by-side comparison of candidate answers with verified reference context.
- **Strengths & Improvement Areas:** Concrete itemized feedback highlighting exact technical gaps.
- **Actionable Recommendations:** AI-curated study priorities tagged by urgency.
- **Downloadable Formal PDF Report:** 1-click export of comprehensive academic interview report.

---

## Slide 12: Remedial Mastery Mode & Targeted Upskilling
**Visual Asset:** `screenshots/12_remedial_mastery_mode.png`

**Transforming Assessment into Active Learning:**
- **Knowledge Graph Root-Cause Tracing:**
  * When candidate scores < 50%, engine queries NetworkX graph for missing prerequisite concepts.
- **Automated AI Curriculum & Study Guide Synthesis:**
  * Generates high-yield study notes, core concepts, and "where candidates typically lose marks".
- **Isolated Prerequisite Knowledge Chunks:**
  * Retrieves exact textbook references for targeted review.
- **1-Click Focused Retest Workflow:**
  * Candidates launch an immediate retest on failed concepts to achieve mastery.

---

## Slide 13: System Verification: 355-Test Matrix (100% Passing)
**Exhaustive Test Coverage Across All 18 Engineering Phases:**
- **355 Total Automated Unit, Integration & Validation Tests (100% Pass Rate in 87.90s):**
  * *Phase 1:* Dense Vector RAG Baseline & S-BERT embeddings (25 tests)
  * *Phase 2-4:* Knowledge Graph Schema, Builder, Storage & Canonical Chunk Resolution (69 tests)
  * *Phase 5:* BM25 Lexical Keyword Retrieval Engine & Tokenization (34 tests)
  * *Phase 6-7:* Graph Traversal Retrieval & Hybrid Reciprocal Rank Fusion (48 tests)
  * *Phase 8:* Reranker Validation & Multi-Signal Scoring (36 tests)
  * *Phase 9-10:* Pipeline Integration & Bloom's Cognitive Progression (39 tests)
  * *Phase 11-13:* Security Audit, Evaluation Metrics & Golden Dataset Auditing (48 tests)
  * *Phase 14-18:* Frozen Baseline, Hybrid Evaluation & Edge Case Safeguards (56 tests)
- **Key Verified Functional Gates:**
  * `TC-01`: Duplicate auth rejected (HTTP 400)
  * `TC-02`: Corrupt uploads safely handled
  * `TC-03`: Sub-25ms retrieval latency
  * `TC-04`: Deterministic Bloom state escalation ($\ge 80\%$) & regression ($< 50\%$)
  * `TC-05`: Remedial graph prerequisite traversal
  * `TC-06`: In-memory Edge-TTS $\le 1.2\text{s}$
  * `TC-07`: 5-signal rubric convergence
  * `TC-08`: Starvation safeguards & fallback handling

---

## Slide 14: Conclusion & Viva Q&A
**Conclusion:**
SmartInterview bridges the gap between theoretical higher education and dynamic industry hiring. By combining Hybrid Graph RAG grounding (Hit@1: 96.97%, Hit@3: 100%), deterministic Bloom's taxonomy cognitive scaffolding, Remedial Mastery drills, and multi-signal objective evaluation, we deliver an authentic, unbiased, low-latency interview preparation ecosystem at zero infrastructure cost.

**Thank You! We are now open for questions and technical discussion from the honorable panel.**
