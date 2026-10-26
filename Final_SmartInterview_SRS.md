# Software Requirement Specification (SRS)

## Personalized Technical Interview Preparation in Higher Education (SmartInterview-G1392)

**Project Team ID: Team G-1392**
1. Shamakura Saiteja Goud - 24BD1A665K
2. Thodsam Srujan - 24BD1A665R
3. Vasireddy Vignesh Reddy - 24BD1A665X
4. Aelugu Ranith Kumar - 25BD5A6615
5. Konduri Abhiram - 25BD5A6620

**Project Mentor:** Dr. TVG Sridevi
**Department:** Computer Science and Engineering (AI & ML)
**Institution:** Keshav Memorial Institute of Technology (KMIT)

---

## Problem Statement
In modern technical recruitment, graduating engineering students face severe preparation barriers including static question banks, anxiety during live technical interviews, lack of personalized feedback, and complete disconnect between university curricula, candidate resumes, and dynamic industry job descriptions. Existing mock interview platforms rely on rigid question sets or ungrounded generative AI bots that hallucinate questions, exhibit significant conversational latency, and lack systematic evaluation methodologies.

When candidates prepare for specific software engineering roles, their target job descriptions require specific technical skillsets—spanning Data Structures, System Design, Operating Systems, Database Management Systems, Computer Networks, and Machine Learning. Static platforms fail to compare candidate resumes against targeted job descriptions to identify exact role overlap and critical skill deficiencies.

Furthermore, traditional evaluation mechanisms fail to measure cognitive depth. When an interview question is presented, candidate responses must be evaluated across multiple technical dimensions—including technical correctness, completeness, conceptual coverage, semantic relevance, and communication clarity. Without dynamic difficulty scaling based on validated educational frameworks, candidates cannot assess their true interview readiness or receive actionable remediation paths.

To overcome these limitations, SmartInterview provides an AI-powered, RAG-grounded adaptive technical mock interview platform. By integrating dense vector retrieval with Bloom's Taxonomy cognitive progression, multi-signal response evaluation, in-memory neural text-to-speech, and automatic speech recognition transcription, the system delivers an authentic, personalized, low-latency interview preparation experience.

---

## 1. Introduction

### 1.1 Purpose
This document specifies the software requirements for Personalized Technical Interview Preparation in Higher Education. The system automates the technical interview preparation lifecycle for engineering candidates. It provides personalized interview sessions grounded in domain-specific computer science knowledge, adjusts question difficulty dynamically based on candidate performance, delivers spoken voice output, transcribes verbal answers, and produces comprehensive analytical evaluation reports.

### 1.2 Product Scope
SmartInterview is an intelligent web-based application designed to bridge the preparation gap between university education and software industry hiring expectations. The platform provides continuous 24x7 self-directed interview practice. Unlike generic chat interfaces, SmartInterview grounds interview content in an authoritative local vector store of exactly 402 curated computer science topic chunks across 50 concepts in 8 foundational technical domains (DSA, DBMS, OS, Computer Networks, System Design, OOP, Design Patterns, and ML/DL). 

The platform supports three distinct operational modes:
1. **Job-Specific Mode:** Ingests candidate resumes and target job descriptions to compute set-theoretic skill overlap (Group A) and role deficiencies (Group B).
2. **Topic-Based Mode:** Provides focused, granular technical drilling across specific selected CS competencies.
3. **Semester Syllabus Mode:** Dynamically isolates vector collections from university syllabus PDFs to align practice directly with upcoming university examinations.

The system conducts dynamic multi-turn technical interviews across Bloom's Revised Taxonomy cognitive tiers, evaluates answers across a 5-factor mathematical rubric, adjusts subsequent question difficulty deterministically, and provides in-memory neural voice delivery alongside downloadable analytical evaluation reports.

### 1.3 References
1. Reimers & Gurevych (2019), "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks."
2. Lewis et al. (2020), "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks."
3. Anderson & Krathwohl (2001), "A Taxonomy for Learning, Teaching, and Assessing: A Revision of Bloom's Taxonomy."
4. Radford et al. (2023), "Robust Speech Recognition via Large-Scale Weak Supervision" (OpenAI Whisper).
5. Groq Inc. (2024), Language Processing Unit (LPU) Hardware Architecture.
6. Nagarajan et al. (Feb 2026), "Development of an Autonomous AI Interview Engine Using Sentence-BERT and Large Language Models for End-to-End Candidate Evaluation."
7. Wahid et al. (March 2026), "AI Mock Interview: An Intelligent Voice-Driven Interview Simulation System using Gemini AI and Whisper."
8. FastAPI and React.js Documentation.

---

## 2. Overall Description

### 2.1 Product Perspective
SmartInterview is an independent, self-contained three-tier web application integrated with local vector retrieval and high-speed cloud inference. The presentation tier consists of a responsive React single-page application; the application tier is powered by a FastAPI backend running under Uvicorn ASGI; the persistence tier utilizes a relational MySQL database for user accounts and session records, and an embedded ChromaDB instance for vector embeddings.

### 2.2 Product Functions
- User registration, authentication with JWT, and profile management.
- Resume upload (PDF) with automated section parsing and skill extraction via PyMuPDF.
- Job description upload (PDF) with Group A (Role Overlap) and Group B (Role Gap) mapping.
- Three configurable interview modes: Job-Specific, Topic-Based, and Dynamic Semester Syllabus.
- Interactive technical mock interviews with real-time text and speech input options.
- Hybrid Graph RAG Tri-Retrieval: Synchronized dense vector search (ChromaDB), lexical keyword search (BM25Okapi), and directed knowledge graph traversal (NetworkX/Neo4j) across 50 concepts in 8 domains.
- Reciprocal Rank Fusion (RRF) and Cross-Encoder Reranking providing authoritative context grounding (Hit@1: 96.97%, Hit@3: 100%, MRR: 0.9798).
- Bloom-levelled single-question generation powered by Groq LPU inference.
- Deterministic adaptive progression adjusting difficulty and cognitive depth after each response (Python state engine).
- Remedial Mastery Mode: Post-interview root-cause prerequisite diagnosis, interactive flashcards, dynamic AI study notes, and targeted retry practice sessions.
- In-memory neural text-to-speech question synthesis via Edge-TTS (<= 1.2s latency).
- Speech-to-text audio transcription via Groq Whisper API (whisper-large-v3) with domain-primed vocabulary.
- Instant multi-signal performance scoring (30% Correctness, 20% Completeness, 20% Relevance, 15% S-BERT Cosine Similarity, and 15% Concept Coverage).
- Comprehensive performance dashboard, remediation roadmaps, and downloadable PDF reports.

### 2.3 Operating Environment
- **Client:** Modern web browser (Chrome, Edge, Firefox, Safari) on Windows, macOS, or Linux. Requires a working microphone interface.
- **Server Runtime:** Python 3.10+ (FastAPI, Uvicorn, SQLAlchemy), Node.js (React, Vite, Tailwind CSS).
- **Database:** MySQL Server 8.0+ and ChromaDB (Local HNSW store).
- **AI Infrastructure:** Groq Cloud API and Microsoft edge-tts.

---

## 3. Specific Requirements

### 3.1 Functional Requirements
- **RI.01.01 Candidate Account Registration:** Secure registration with bcrypt password hashing.
- **RI.01.02 Candidate Authentication:** Issue HS256-signed JWTs valid for 24 hours.
- **RI.01.03 Resume Ingestion & PDF Parsing:** Extract skills and experience using PyMuPDF.
- **RI.01.04 Job Description Upload & Role Extraction:** Parse required qualifications and technical responsibilities.
- **RI.01.05 Skill Overlap and Gap Mapping:** Compute intersection/difference to identify overlapping skills and gaps.
- **RI.01.06 RAG-Grounded Bloom-Adaptive Question Generation:** Retrieve top context chunks from ChromaDB and prompt the LLM to generate exactly one contextual technical question.
- **RI.01.07 Multi-Signal 5-Factor Answer Evaluation:** Produce an overall score based on Technical Correctness (30%), Completeness (20%), Relevance (20%), Semantic Similarity via SentenceTransformers (15%), and Concept Coverage (15%).
- **RI.01.08 Deterministic Adaptive State Progression:** Score >= 80% advances Bloom level (+1); 50% <= Score < 80% maintains level; Score < 50% regresses Bloom level (-1).
- **RI.01.09 Neural Text-to-Speech Question Streaming:** Synthesize and stream audio in-memory to the client.
- **RI.01.10 Whisper Speech-to-Text Answer Transcription:** Accept recorded audio and return verbatim transcribed text.
- **RI.01.11 Downloadable PDF Interview Report:** Generate a comprehensive post-interview report detailing performance and progression.
- **RI.01.12 Hybrid Graph RAG Retrieval:** Simultaneously execute dense vector search, BM25Okapi lexical matching, and directed knowledge graph prerequisite traversal, fusing results via Reciprocal Rank Fusion (RRF).
- **RI.01.13 Remedial Mastery Weakness Diagnosis:** Automatically trace failed questions back through the knowledge graph to detect missing prerequisite concepts.
- **RI.01.14 Dynamic Study Notes & Flashcards:** Generate targeted revision summaries, micro-lessons, and interactive flashcards for diagnosed weaknesses.
- **RI.01.15 Targeted Retry Drills:** Launch focused practice mini-sessions allowing candidates to re-attempt failed concepts until mastery is confirmed.
- **RI.01.16 Remediation PDF Report:** Produce downloadable diagnostic remediation roadmaps with visual radar analytics.

### 3.2 Non-Functional Requirements
- **Performance:** Semantic Search Latency <= 100ms (Benchmark: 24.6 ms). Speech-to-Text Transcription Latency <= 1.5s. TTS Streaming Latency <= 1.2 seconds (In-memory `io.BytesIO`). Total End-to-End Turnaround Latency < 2.5 seconds (Groq LPU 320ms TTFT).
- **Security:** JWT authentication (HS256, 24h expiration), bcrypt password hashing (work factor 12), and rigorous file upload sanitization (<= 5MB).
- **Robustness:** Fallback text input in case of microphone failure; API key decoupling with dual-model failover (`openai/gpt-oss-120b` to `openai/gpt-oss-20b`).

---

## Software Development Life Cycle (SDLC)
The Software Development Life Cycle (SDLC) followed for SmartInterview is the Agile/Iterative Methodology. 
- **Stage 1 (Planning & Requirement Analysis):** Feasibility study on deploying local vector embeddings vs. cloud models to minimize latency. 
- **Stage 2 (Defining Requirements):** Formulation of this SRS to lock in functional scopes like Bloom's scaling, 3 operational modes, and RAG indexing.
- **Stage 3 (Designing Product Architecture):** Establishing a decoupled 4-tier structure (React SPA, FastAPI, MySQL + ChromaDB).
- **Stage 4 (Building):** Implementation of modular microservices (Auth, Resume Parsing, RAG Querying, TTS/STT integration).
- **Stage 5 (Testing):** Unit testing of scoring rubrics and semantic similarity thresholds to ensure accuracy.
- **Stage 6 (Deployment):** Staging behind a Uvicorn ASGI server and exposing client endpoints.

---

## Literature Survey
1. **Base Paper 1 — Nagarajan et al. (Feb 2026, IJMRR):** "Development of an Autonomous AI Interview Engine Using Sentence-BERT and Large Language Models for End-to-End Candidate Evaluation." Employs Sentence-BERT (`all-MiniLM-L6-v2`) and cosine similarity for ATS resume-to-JD matching and Web Speech API for two-way voice screening. Built as an exclusionary corporate recruiter tool lacking student diagnostic feedback, code sandboxes, or curriculum grounding.
2. **Base Paper 2 — Wahid et al. (March 2026, IJERT):** "AI Mock Interview: An Intelligent Voice-Driven Interview Simulation System using Gemini AI and Whisper." Built for student mock interviews with Streamlit, Gemini API, OpenAI Whisper (16 kHz), and ReportLab PDF roadmaps. Suffers from one-way voice interaction (no TTS speech output) and rigid domain dropdowns without custom JD matching.
3. **Sentence-BERT (Reimers & Gurevych, 2019):** Modified pre-trained BERT networks using siamese and triplet structures for deriving semantically meaningful sentence embeddings. Applied in SmartInterview for local high-speed semantic similarity scoring (15% weight) and JD matching.
4. **Retrieval-Augmented Generation (Lewis et al., 2020):** Combined parametric memory with non-parametric memory to reduce hallucinations. SmartInterview uses this to ground the Groq LLM against a curated ChromaDB of exactly 402 CS topic chunks across 50 concepts in 8 domains, achieving 96.97% Hit@1, 100% Hit@3, and 0.9798 MRR.
5. **Bloom's Revised Taxonomy (Anderson & Krathwohl, 2001):** Revised cognitive taxonomy (Remember, Understand, Apply, Analyze, Evaluate, Create) utilized as the deterministic state machine for interview progression.
6. **OpenAI Whisper (Radford et al., 2023):** State-of-the-art zero-shot STT, integrated into SmartInterview via Groq Cloud (`whisper-large-v3`) with domain-primed vocabulary prompting.
7. **Language Processing Unit (Groq Inc., 2024):** High-speed tensor processing architecture allowing the application to achieve sub-second LLM inference times during live conversations.

---

## 4. System Designing & UML Diagrams

### 4.1 Use Case Diagram
```mermaid
graph LR
    C[Candidate] --> A1(Register / Login)
    C --> A2(Upload Resume & JD)
    C --> A3(Start Interview)
    C --> A4(Answer Question Text/Voice)
    C --> A5(Download PDF Report)
    
    A3 -->|RAG retrieval| DB2[(ChromaDB)]
    A3 -->|Generate| G[Groq Cloud LLM]
    A4 -->|Transcribe| W[Whisper STT]
    A4 -->|Evaluate| G
```

### 4.2 Sequence Diagram: Interview Session & Evaluation
```mermaid
sequenceDiagram
    participant C as Candidate
    participant F as React UI
    participant A as FastAPI Server
    participant V as ChromaDB
    participant LLM as Groq Cloud API

    C->>F: Start Interview (Select Skill)
    F->>A: POST /interviews/start
    A->>V: Query semantic chunks for Skill
    V-->>A: Top-3 relevant context chunks
    A->>LLM: Generate Question (Prompt + Context + Bloom Level)
    LLM-->>A: Technical Question
    A-->>F: Return Question (with TTS audio)
    F-->>C: Display Question & Play Audio
    
    C->>F: Provide Answer (Voice/Text)
    F->>A: POST /interviews/answer
    A->>LLM: Evaluate Answer (Multi-factor)
    LLM-->>A: Evaluation Scores & Feedback
    A->>A: Update Bloom Level based on Score
    A-->>F: Return Result & Next Question
```

### 4.3 Class Diagram
```mermaid
classDiagram
    class User {
        +UUID id
        +String email
        +String password_hash
    }
    class Resume {
        +UUID id
        +String filename
        +JSON skills
    }
    class JobDescription {
        +UUID id
        +JSON required_skills
    }
    class InterviewSession {
        +UUID id
        +String status
        +Int current_bloom_level
    }
    class Question {
        +String text
        +String skill
    }
    class Answer {
        +String answer_text
        +Float score
    }
    
    User "1" -- "*" Resume
    User "1" -- "*" JobDescription
    User "1" -- "*" InterviewSession
    InterviewSession "1" -- "*" Question
    Question "1" -- "1" Answer
```

### 4.4 Statechart Diagram (Bloom's Taxonomy Progression)
```mermaid
stateDiagram-v2
    direction TB
    state "Level 1: Remember" as L1
    state "Level 2: Understand" as L2
    state "Level 3: Apply" as L3
    
    [*] --> L1: Start Session
    L1 --> L2: Score >= 80%
    L2 --> L3: Score >= 80%
    L2 --> L1: Score < 50%
    L3 --> L2: Score < 50%
    
    L1 --> L1: 50% <= Score < 80%
    L2 --> L2: 50% <= Score < 80%
```

### 4.5 Activity Diagram (End-to-End Lifecycle)
```mermaid
stateDiagram-v2
    [*] --> Login
    Login --> UploadDocs: Upload Resume / Job Description
    UploadDocs --> StartInterview
    StartInterview --> GenerateQuestion: RAG + LLM Integration
    GenerateQuestion --> PresentQuestion: Voice/Text Output
    PresentQuestion --> CaptureAnswer: Speech/Text Input
    CaptureAnswer --> EvaluateAnswer: 5-Factor Scoring Model
    EvaluateAnswer --> UpdateBloomLevel: Adjust Difficulty
    UpdateBloomLevel --> GenerateQuestion: Loop if Questions Remain
    UpdateBloomLevel --> FinishInterview: If Complete
    FinishInterview --> GenerateReport: PDF Analytics
    GenerateReport --> [*]
```

### 4.6 Entity Relationship Diagram (ERD)
```mermaid
erDiagram
    USERS ||--o{ RESUMES : uploads
    USERS ||--o{ JOB_DESCRIPTIONS : uploads
    USERS ||--o{ INTERVIEW_SESSIONS : conducts
    INTERVIEW_SESSIONS ||--|{ INTERVIEW_QUESTIONS : contains
    INTERVIEW_QUESTIONS ||--o| ANSWERS : receives

    USERS {
        uuid id PK
        string email
        string password_hash
    }
    INTERVIEW_SESSIONS {
        uuid id PK
        uuid user_id FK
        string status
        int current_bloom_level
    }
```

### 4.7 Deployment Diagram
```mermaid
graph TD
    subgraph Client
        Browser[Web Browser - React SPA]
    end
    subgraph Application Server
        API[FastAPI Server - Python]
    end
    subgraph Local Storage
        DB[(MySQL 8.0)]
        VectorDB[(ChromaDB)]
    end
    subgraph External Cloud Services
        Groq[Groq Cloud LLM API]
        Whisper[Whisper STT]
        EdgeTTS[Microsoft Edge TTS]
    end

    Browser -->|HTTPS| API
    API -->|SQLAlchemy| DB
    API -->|Local File IO| VectorDB
    API -->|HTTPS| Groq
    API -->|HTTPS| Whisper
    API -->|HTTPS| EdgeTTS
```

---

## 5. Implementation
- **Frontend Architecture:** React 18/19, Vite, Tailwind CSS v4, Context API for state management, interactive remediation study dashboard (`Remediation.jsx`, `RemediationModal.jsx`).
- **Backend Services:** FastAPI 0.115, Python 3.10+, Uvicorn ASGI, modular routing (`auth`, `resumes`, `interviews`, `remediation_service`, `report_service`).
- **Hybrid Graph RAG Engine:** Tri-retrieval pipeline featuring ChromaDB (dense semantic vectors), rank-bm25 (BM25Okapi lexical matching), and NetworkX/Neo4j (directed knowledge graph store). Results merged via Reciprocal Rank Fusion (RRF) and scored via cross-encoder reranking.
- **Remedial Mastery Engine:** Knowledge Graph root-cause tracing, automated micro-lesson generation, interactive flashcard synthesis, and targeted retry practice drill generation.
- **Generative AI & Inference:** Groq Cloud LPU architecture for high-speed inference.
- **Voice Processing Subsystem:** Microsoft edge-tts for speech synthesis and Whisper-large-v3 for transcription.

---

## 6. Testing (Validation & Verification)
**Software Validation:** Ensures the platform satisfies user needs. Tests confirmed that candidates can seamlessly upload a resume and JD, triggering an interview accurately mapped to their role overlapping and gap areas, and proceed to remedial practice upon session completion.
**Software Verification:** Confirms adherence to design. Evaluated API schemas, foreign key constraints in MySQL, mathematical verification of the 5-factor weighting formula, and 274 unit/integration tests across 18 phases for the Hybrid Graph RAG pipeline.

| Test ID | Module | Scenario | Expected Result | Status |
|---|---|---|---|---|
| TC-01 | Auth | Register duplicate user | HTTP 400 Bad Request | PASSED |
| TC-02 | Resume | Upload invalid file type | HTTP 400 Rejected | PASSED |
| TC-03 | Hybrid RAG | Tri-Retrieval Fusion (Vector+BM25+Graph) | Fused RRF candidate ranking (latency <= 650ms) | PASSED |
| TC-04 | Graph Store | Neo4j unreachable / uninstalled | Graceful fallback to embedded NetworkX | PASSED |
| TC-05 | Adaptive | Score >= 80% | Bloom tier advances (+1) | PASSED |
| TC-06 | Adaptive | Score < 50% | Bloom tier regresses (-1) | PASSED |
| TC-07 | Remediation | Session score < 70% | Generates root-cause prerequisite diagnosis | PASSED |
| TC-08 | Voice | Synthesize TTS stream | Audio byte stream OK (latency <= 1.2s) | PASSED |
| TC-09 | Evaluation | 5-Factor Scoring Formula | Deterministic mathematical score convergence | PASSED |
| TC-10 | Benchmark | 274 Suite RAG Phase Tests | 274/274 unit and integration tests passing | PASSED |

---

## 7. Conclusion
SmartInterview successfully demonstrates the integration of Retrieval-Augmented Generation (RAG) with a deterministic adaptive learning engine based on Bloom's Revised Taxonomy, resolving the fundamental flaws of static question banks and hallucinatory AI interview bots. By enforcing domain-filtered retrieval across curated computer science topics, the system guarantees technical grounding. The hybrid 5-signal evaluation architecture provides objective, transparent scoring, delivering a robust, accessible, and pedagogically sound interview preparation experience.
