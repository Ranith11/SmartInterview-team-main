<div align="center">
  <div style="width: 80px; height: 80px; background-color: #4f46e5; border-radius: 20px; display: flex; align-items: center; justify-content: center; margin-bottom: 20px;">
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
  </div>
  
  # SmartInterview

  **An Adaptive, AI-Powered Technical Interview & Examination Preparation Platform**
  *Powered by Hybrid Graph RAG & Dynamic Remedial Mastery*

  [![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
  [![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
  [![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
  [![Groq](https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com/)
  [![ChromaDB](https://img.shields.io/badge/ChromaDB-FF6F00?style=for-the-badge&logo=databricks&logoColor=white)](https://trychroma.com/)
  [![NetworkX](https://img.shields.io/badge/NetworkX-007acc?style=for-the-badge&logo=python&logoColor=white)](https://networkx.org/)

</div>

<br />

SmartInterview revolutionizes how students and professionals prepare for technical assessments. By bridging the gap between passive studying and high-pressure recall, the platform provides hyper-realistic, dynamic mock interviews tailored explicitly to your target role, university syllabus, or technical curriculum.

SmartInterview operates on a ground-breaking **Hybrid Graph Retrieval-Augmented Generation (Hybrid Graph RAG)** pipeline and an automated **Remedial Mastery Mode**—preventing AI hallucinations, testing deep relational prerequisites, and dynamically prescribing personalized study plans when candidates struggle.

---

## 🌟 Core System Capabilities

### 1. 🧠 Multi-Stage Hybrid Graph RAG Pipeline
Unlike conventional mock interview bots that rely solely on superficial vector similarity, SmartInterview combines three synchronized retrieval engines:
- **Dense Vector Search (ChromaDB):** Captures semantic intent and natural-language meaning via Siamese Sentence-BERT (`all-MiniLM-L6-v2`) embeddings.
- **Lexical BM25 Search (`rank-bm25`):** Accurately captures exact technical keywords, error codes, and acronyms (`2PL`, `ACID`, `O(V+E)`, `CAS`).
- **Knowledge Graph Traversal (`NetworkX` / `Neo4j`):** Navigates a structured directed graph of 50 CS concepts and prerequisite edges across 8 foundational domains. Understands dependencies (`prerequisite_of`, `subtopic_of`, `applied_in`).
- **Reciprocal Rank Fusion (RRF) & Cross-Encoder Reranker:** Combines and normalizes candidate candidates using rank reciprocal math ($RRF(d) = \sum \frac{1}{k + r(d)}$) to pass authoritative ground-truth context to the LLM.

### 2. 🎯 Remedial Mastery Mode & Diagnostic Study Plans
Mock interviews are useless if you don't learn from mistakes. SmartInterview includes an automated remediation engine:
- **Root-Cause Prerequisite Diagnosis:** Automatically traces question failures back through the Knowledge Graph to identify the root concept the candidate lacked.
- **Dynamic AI Study Notes & Flashcards:** Instantly generates structured revision cards, conceptual summaries, and common pitfalls for identified weak topics.
- **Targeted Retry Drills:** Spawns targeted mini-sessions allowing candidates to immediately re-attempt failed concepts until verified mastery is achieved.
- **Downloadable Remediation PDF:** Export comprehensive diagnostic reports with performance radar charts and remediation roadmaps.

### 3. 🎯 Targeted Resume vs. Job Description Analysis
- Upload candidate Resume (PDF) and target Job Description (PDF).
- PyMuPDF extracts skill inventories and calculates set-theoretic mapping:
  - **Group A (Role Overlap):** Skills present in both resume and JD (validated for depth).
  - **Group B (Critical Skill Gaps):** Missing competencies demanded by the employer (targeted for rigorous testing).

### 4. 📈 Dynamic Bloom's Taxonomy Adaptive Scaling
Questions scale through educational cognitive tiers:
$$\text{Remember} \longrightarrow \text{Understand} \longrightarrow \text{Apply} \longrightarrow \text{Analyze} \longrightarrow \text{Evaluate} \longrightarrow \text{Create}$$
- Scores $\ge 80\%$: Promotes difficulty and complexity to higher-order architectural questions.
- Scores $\le 50\%$: Steers downwards to foundational concepts, activating remediation hints.

### 5. 🎙️ Real-Time Spoken Conversational Experience
- **Edge-TTS Neural Synthesis:** Synthesizes voice audio in-memory (`io.BytesIO`) in $\le 1.2\text{s}$ with natural cadence.
- **Groq Whisper ASR (`whisper-large-v3`):** High-accuracy transcription tailored with technical computer science vocabulary prompts.

---

## 🏗️ System Architecture

```
                                  [ Candidate Browser (React + Vite + Tailwind CSS) ]
                                              │                                ▲
                                       REST / JSON                   Audio / Spoken Output
                                              ▼                                │
                        ┌──────────────────────────────────────────────────────────────┐
                        │                 FastAPI Application Tier                     │
                        ├──────────────────────────────┬───────────────────────────────┤
                        │    Interview Orchestrator    │    Remedial Mastery Engine    │
                        │    (Bloom Adaptive Engine)   │    (Weakness Diagnosis & PDF) │
                        └──────────────┬───────────────┴───────────────┬───────────────┘
                                       │                               │
                                       ▼                               ▼
                        ┌──────────────────────────────────────────────────────────────┐
                        │             Hybrid Graph RAG Retrieval Engine                │
                        │                                                              │
                        │   ┌────────────────┐   ┌───────────────┐   ┌─────────────┐   │
                        │   │ Vector Search  │   │  BM25 Lexical │   │ Graph Store │   │
                        │   │   (ChromaDB)   │   │  (rank-bm25)  │   │ (NetworkX)  │   │
                        │   └───────┬────────┘   └───────┬───────┘   └──────┬──────┘   │
                        │           │                    │                  │          │
                        │           └──────────────┬─────┴──────────────────┘          │
                        │                          ▼                                   │
                        │            Reciprocal Rank Fusion (RRF)                      │
                        │                          ▼                                   │
                        │            Cross-Encoder Reranker (Top-3)                    │
                        └──────────────────────────┬───────────────────────────────────┘
                                                   │
                                                   ▼
                               [ Groq LPU Inference (Llama 3.3 / 70B) ]
```

---

## 🚀 Quick Start Guide

### Prerequisites
- Node.js (v18+)
- Python (3.10+)
- A [Groq API Key](https://console.groq.com/keys)

### 1. Clone & Environment Setup
```bash
git clone https://github.com/yourusername/Smart-Interview-main.git
cd Smart-Interview-main

# Setup environment variables
cp .env.example .env
# Edit .env and insert your GROQ_API_KEY
```

Key environment configuration options in `.env`:
```env
GROQ_API_KEY=your_groq_api_key_here
RAG_MODE=hybrid                      # options: hybrid, dense, keyword, graph
GRAPH_STORAGE_BACKEND=networkx       # options: auto, networkx, neo4j
RERANKER_ENABLED=true                # options: true, false
HYBRID_FUSION_METHOD=weighted        # options: weighted, rrf
```

### 2. Backend Installation & Startup
```bash
# Activate your Python virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install all backend requirements (including networkx & rank-bm25)
pip install -r backend/requirements.txt

# Start the FastAPI backend server
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
*API Swagger Documentation will be available live at `http://localhost:8000/docs`.*

### 3. Frontend Installation & Startup
Open a separate terminal:
```bash
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
*The web interface will be accessible at `http://localhost:5173`.*

---

## 🧪 Comprehensive Verification & Test Suite

The project includes an extensive suite of **274 unit and integration tests across 18 phases**, verifying schema contracts, BM25 exact matching, graph traversal, and failure recovery.

Run the test suite:
```bash
# Run all RAG core and integration tests
pytest tests/test_phase*.py -v

# Run benchmark evaluations
python scripts/benchmark_hybrid_rag.py
```

### Empirical Retrieval Benchmark Highlights
Tested against ground-truth technical queries across 8 core domains:
- **Hit@1:** $96.97\%$ (Dense Baseline: $84.2\%$)
- **Hit@3:** $100.0\%$ (Dense Baseline: $91.5\%$)
- **Mean Reciprocal Rank (MRR):** $0.9798$
- **Knowledge Graph Traversal Latency:** $< 12\text{ms}$ (in-memory NetworkX)
- **End-to-End Pipeline Latency:** $< 650\text{ms}$

---

## 👥 Project Team & Academic Credits

**Institution:** Keshav Memorial Institute of Technology (KMIT)  
**Department:** Computer Science and Engineering (AI & ML)  
**Project Mentor:** Dr. TVG Sridevi  
**Project Team G-1392:**
- Konduri Abhiram (25BD5A6620)
- Shamakura Saiteja Goud (24BD1A665K)
- Thodsam Srujan (24BD1A665R)
- Vasireddy Vignesh Reddy (24BD1A665X)
- Aelugu Ranith Kumar (25BD5A6615)