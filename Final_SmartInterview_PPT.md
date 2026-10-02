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
- Existing AI bots frequently hallucinate facts, exhibit conversational latency, and lack systematic evaluation rubrics.

**The Gap:** Candidates cannot accurately assess their interview readiness or receive actionable feedback mapped to the roles they are actually applying for.

---

## Slide 3: Proposed Solution
**SmartInterview: An AI-Powered, Adaptive Mock Interview Platform**
- **Context-Aware:** Compares candidate resumes directly against target job descriptions to identify exact role overlaps and critical skill deficiencies.
- **RAG-Grounded:** Retrieves information from curated technical knowledge bases to generate accurate interview questions and eliminate AI hallucinations.
- **Adaptive Learning:** Dynamically scales question difficulty based on Bloom's Taxonomy cognitive tiers.
- **Multi-Signal Evaluation:** Continuously evaluates student performance across technical correctness, response quality, and communication clarity.

---

## Slide 4: System Architecture
**Decoupled, High-Performance Technology Stack:**
- **Frontend Layer:** React.js Single Page Application (SPA), providing a highly interactive and low-latency user interface.
- **Application Logic:** FastAPI (Python) serving as the robust backend API gateway.
- **Vector Grounding (RAG):** ChromaDB stores pre-indexed computer science chunks; Sentence-BERT generates dense semantic embeddings locally.
- **Generative Inference:** Llama 3 / GPT-OSS models via Groq Cloud deliver sub-second question generation and evaluation.
- **Voice Subsystem:** Microsoft edge-tts for in-memory neural speech streaming and OpenAI Whisper API for near-instant transcription.
- **Persistence:** MySQL Relational Database handling stateless JWT authentication and session tracking.

---

## Slide 5: Core Workflow & Context Ingestion
**How SmartInterview personalizes the experience:**
1. **Document Ingestion:** Candidate uploads a Resume (PDF) and a target Job Description.
2. **Deterministic Extraction:** High-speed extraction isolates technical skills from both documents.
3. **Skill Gap Analysis:**
   - **Group A (Role Overlap):** Validates skills present in both the resume and JD.
   - **Group B (Role Gaps):** Highlights skills required by the JD but missing from the resume.
4. **Targeted Staging:** The interview dynamically focuses on verifying Group A and testing the candidate's adaptability for Group B.

---

## Slide 6: RAG-Grounded Question Generation
**Preventing LLM Hallucinations:**
- **The Issue:** Standard LLMs invent functions, frameworks, or incorrect algorithmic complexities.
- **Our Approach (RAG):** We pre-indexed 400+ curated computer science topics spanning 8 domains (DSA, DBMS, OS, Computer Networks, System Design, etc.).
- **Execution:** When testing a specific skill, the system queries ChromaDB using Cosine Similarity to find the Top-3 verified reference chunks.
- **Generation:** These chunks are sent to the LLM, forcing the AI to generate a technical question strictly bounded by factual, verified literature.

---

## Slide 7: Deterministic Adaptive Progression (Bloom's Taxonomy)
**Strict Cognitive Difficulty Scaling:**
- We removed arbitrary LLM difficulty jumps in favor of a deterministic Python state machine mapped to **Bloom’s Revised Taxonomy** (Remember, Understand, Apply, Analyze, Evaluate, Create).
- **The Logic:**
  - **Score >= 80% (Mastery):** Advance to a higher cognitive tier (e.g., from "Understand" to "Apply").
  - **Score 50% - 79% (Adequate):** Maintain the current difficulty level.
  - **Score < 50% (Remediation):** Regress to a previous tier to rebuild foundational concepts.
- **Result:** A consistent, fair, and pedagogically sound interview progression.

---

## Slide 8: Multi-Signal Answer Evaluation
**Objective, Multi-Dimensional Scoring:**
- Instead of a single, highly-variable AI score, answers are evaluated using a strict weighted formula:
  - **30% Technical Correctness** (LLM critique)
  - **20% Completeness** (Addressed all constraints)
  - **20% Relevance** (Focus and conciseness)
  - **15% Semantic Similarity** (Sentence-BERT matching candidate answer against ground-truth)
  - **15% Concept Coverage** (Keyword extraction)
- This hybrid model balances semantic conceptual understanding with LLM technical reasoning.

---

## Slide 9: Voice Interaction & Final Reporting
**Creating an Authentic Interview Environment:**
- **Voice-In / Voice-Out:** Candidates speak their answers into the browser (transcribed via Whisper STT) and hear the interviewer's questions naturally spoken (synthesized via edge-tts).
- **Performance Analytics:** A dynamic React dashboard displays real-time skill performance and Bloom level distribution.
- **PDF Report Generation:** Post-interview, the platform auto-generates a downloadable, multi-page PDF report detailing the exact transcripts, skill proficiencies, and targeted learning recommendations.

---

## Slide 10: Conclusion & Future Scope
**Conclusion:**
SmartInterview successfully resolves the core flaws of static question banks and unreliable AI mock interviewers. By merging Retrieval-Augmented Generation with rigorous pedagogical models (Bloom's Taxonomy) and multi-factor evaluation, we deliver a highly realistic, responsive, and unbiased interview preparation ecosystem.

**Future Scope:**
- Expansion into behavioral (HR) and system-design whiteboard modes.
- Integration of live coding execution environments (compilers).
- Emotion and sentiment analysis via computer vision for body language assessment.

---

## Slide 11: Questions & Answers
**Thank You!**
We are now open to any questions regarding the system architecture, RAG implementation, or adaptive algorithms.
