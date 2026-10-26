import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(REPO_ROOT, "docs", "final_deliverables")
os.makedirs(OUT_DIR, exist_ok=True)


def build_pptx():
    prs = Presentation()
    # Set to 16:9 widescreen
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    def add_slide(title_text, bullets):
        slide = prs.slides.add_slide(prs.slide_layouts[1]) # Title & Content layout
        title = slide.shapes.title
        title.text = title_text
        title.text_frame.paragraphs[0].font.size = Pt(28)
        title.text_frame.paragraphs[0].font.bold = True
        title.text_frame.paragraphs[0].font.color.rgb = RGBColor(26, 54, 93) # Navy blue

        body = slide.placeholders[1]
        tf = body.text_frame
        tf.word_wrap = True
        
        # Clear default placeholder text
        p_first = tf.paragraphs[0]
        p_first.text = ""

        for idx, line in enumerate(bullets):
            if idx == 0:
                p = p_first
            else:
                p = tf.add_paragraph()
            
            p.text = line.strip()
            if line.startswith("• ") or line.startswith("- "):
                p.level = 0
                p.font.size = Pt(17)
                p.space_after = Pt(6)
            elif line.startswith("   - ") or line.startswith("  * "):
                p.level = 1
                p.font.size = Pt(15)
                p.space_after = Pt(4)
            elif line.endswith(":") or line.startswith("###") or "Benchmark" in line or "Scoring" in line:
                p.level = 0
                p.font.bold = True
                p.font.size = Pt(18)
                p.font.color.rgb = RGBColor(43, 108, 176)
                p.space_after = Pt(8)
            else:
                p.level = 0
                p.font.size = Pt(16)
                p.space_after = Pt(6)
        return slide

    # Slide 1: Title Slide
    s1 = prs.slides.add_slide(prs.slide_layouts[0])
    s1.shapes.title.text = "SmartInterview"
    s1.shapes.title.text_frame.paragraphs[0].font.size = Pt(40)
    s1.shapes.title.text_frame.paragraphs[0].font.bold = True
    s1.shapes.title.text_frame.paragraphs[0].font.color.rgb = RGBColor(26, 54, 93)
    
    sub = s1.placeholders[1]
    sub.text = (
        "Personalized Technical Interview Preparation in Higher Education\n"
        "Team ID: Team G-1392 | Department of CSE (AI & ML)\n"
        "Keshav Memorial Institute of Technology (KMIT)\n"
        "Faculty Mentor: Dr. TVG Sridevi"
    )
    for p in sub.text_frame.paragraphs:
        p.font.size = Pt(18)

    # Slide 2: Introduction & Problem Statement
    add_slide(
        "Introduction & Literature Gaps",
        [
            "The Challenge in Technical Campus Recruitment:",
            "• Disconnect between static academic curricula and dynamic industry job descriptions.",
            "• High student anxiety, lack of verbal articulation practice, and high placement attrition.",
            "Gaps Identified in Foundational 2026 Literature:",
            "• Base Paper 1 (Nagarajan et al., Feb 2026): Enterprise recruiter screening filter; lacks candidate feedback, diagnostic reports, code sandboxes, or curriculum grounding.",
            "• Base Paper 2 (Wahid et al., March 2026): Voice is strictly one-way (silent AI, student reads text); rigid domain dropdowns without custom JD matching.",
            "• Core Gap: Students lack a grounded, low-latency, two-way conversational coach with objective scoring."
        ]
    )

    # Slide 3: Proposed Solution
    add_slide(
        "Proposed Solution: SmartInterview",
        [
            "An AI-Powered, Adaptive Mock Interview Platform for Higher Education:",
            "• Three Distinct Operational Modes:",
            "   - Job-Specific Mode: Set-theoretic Resume-to-JD mapping (Group A Overlap vs. Group B Gaps).",
            "   - Topic-Based Mode: Granular technical drilling across chosen computer science domains.",
            "   - Semester Syllabus Mode: Isolated vector collections generated dynamically from syllabus PDFs.",
            "• Curated RAG Grounding: ChromaDB over 402 CS chunks to eliminate hallucinations at the root.",
            "• Deterministic Cognitive Scaffolding: Pedagogical progression via Bloom's Revised Taxonomy.",
            "• Multi-Signal 5-Factor Evaluation: Eliminates subjective black-box LLM 'vibe grading'."
        ]
    )

    # Slide 4: System Architecture
    add_slide(
        "Decoupled 4-Tier Distributed Architecture",
        [
            "High-Performance, Low-Latency Technology Stack:",
            "• Presentation Tier: React 18 SPA (Vite, Tailwind CSS, Web Speech API audio visualizer).",
            "• Application Routing: FastAPI (Python 3.10+, Uvicorn ASGI, Pydantic v2, HS256 JWT auth).",
            "• Core Intelligence Tier:",
            "   - ChromaDB HNSW Vector Store ('technical_kb', 402 chunks, 384-dim S-BERT embeddings).",
            "   - Groq Cloud LPU Inference (Llama 3.3 70B / GPT-OSS 120B, 320ms TTFT).",
            "   - Deterministic Python Bloom Adaptive State Engine.",
            "• Voice Subsystem & Persistence:",
            "   - Microsoft Edge-TTS (en-US-ChristopherNeural, in-memory io.BytesIO, <= 1.2s latency).",
            "   - Whisper Large-v3 STT with domain-primed technical vocabulary prompt.",
            "   - MySQL 8.0 relational database for users, sessions, and transcripts."
        ]
    )

    # Slide 5: Core Workflow & Context Ingestion
    add_slide(
        "Core Workflow & Context Ingestion",
        [
            "Personalized Technical Staging Pipeline:",
            "• Document Ingestion: Candidate uploads Resume (PDF) and target Job Description (or Syllabus).",
            "• Deterministic Extraction: PyMuPDF isolates technical competencies and experience entities.",
            "• Set-Theoretic Skill Gap Analysis:",
            "   - Group A (Role Overlap): Skills present in both Resume & JD -> Targeted for verification.",
            "   - Group B (Role Gaps): Skills required by JD but missing in Resume -> Targeted for adaptability.",
            "• Targeted Staging: The interview dynamically focuses on validating Group A and bridging Group B."
        ]
    )

    # Slide 6: RAG-Grounded Question Generation
    add_slide(
        "RAG Grounding: Eliminating Hallucinations",
        [
            "Knowledge Base Architecture:",
            "• Curated repository of exactly 402 validated CS chunks across 50 concepts in 8 core domains (DSA, DBMS, OS, CN, System Design, OOP, Design Patterns, ML/DL).",
            "Empirical Retrieval Benchmarks (33 Technical Domain Queries):",
            "• Hit@1 = 96.97% (Top retrieved chunk is the exact ground-truth answer key).",
            "• Hit@3 = 100.00% (Correct technical reference chunk guaranteed in top 3).",
            "• Mean Reciprocal Rank (MRR) = 0.9798 (Near-perfect ranking precision).",
            "• Retrieval Latency = 24.6 ms (Sub-100ms vector search via local ChromaDB HNSW).",
            "• Result: Zero ungrounded algorithmic or framework hallucinations."
        ]
    )

    # Slide 7: Deterministic Adaptive Progression
    add_slide(
        "Deterministic Adaptive Engine (Bloom's Taxonomy)",
        [
            "Pedagogical Cognitive Scaffolding (Python State Machine):",
            "• Maps questions strictly across Bloom's Revised Taxonomy:",
            "  Remember (L1) -> Understand (L2) -> Apply (L3) -> Analyze (L4) -> Evaluate (L5) -> Create (L6).",
            "Deterministic Transition Rules:",
            "• Score >= 80% (Mastery): Advance Bloom cognitive level (+1) or advance difficulty tier.",
            "• Score 50% - 79% (Adequate): Maintain current Bloom level and difficulty tier.",
            "• Score < 50% (Remediation): Regress Bloom level (-1) to rebuild core foundational concepts.",
            "• Weakness-Biased Skill Selection: Automatically samples next questions from lowest-scoring skills."
        ]
    )

    # Slide 8: Multi-Signal Answer Evaluation
    add_slide(
        "Multi-Signal Evaluation (Eliminating 'Vibe Grading')",
        [
            "Objective 5-Part Mathematical Scoring Rubric:",
            "• 30% Technical Correctness: Deep LLM logical reasoning and factual accuracy.",
            "• 20% Completeness: Direct coverage of all question constraints and edge cases.",
            "• 20% Relevance: Focus, conciseness, and elimination of conversational filler.",
            "• 15% Semantic Cosine Similarity: Sentence-BERT (all-MiniLM-L6-v2) matching against ground truth.",
            "• 15% Explicit Concept Coverage: Deterministic keyword & technical entity detection.",
            "Why This Split? Blends semantic understanding with hard concept verification, ensuring reproducible, unbiased scoring immune to prompt drift."
        ]
    )

    # Slide 9: Voice Pipeline & Comprehensive Reporting
    add_slide(
        "Voice Pipeline & Comprehensive Reporting",
        [
            "Low-Latency Spoken Dialogue Pipeline:",
            "• Two-Way Audio: Whisper Large-v3 STT (Groq) + Microsoft Edge-TTS (en-US-ChristopherNeural).",
            "• Voice Synthesis Latency <= 1.2s: In-memory io.BytesIO streaming (zero disk footprint).",
            "• End-to-End Turnaround < 2.5s: Prevents conversational dead air during mock interviews.",
            "Diagnostic Performance Reporting:",
            "• Real-time React dashboard with 5-axis competency radar chart & Bloom level progression.",
            "• Downloadable ReportLab PDF: Detailed question transcripts, skill heatmaps, and personalized upskilling roadmaps."
        ]
    )

    # Slide 10: System Verification & Test Matrix
    add_slide(
        "System Verification & Test Matrix",
        [
            "Validated across 7 formal test cases (TC-01 through TC-07):",
            "• TC-01 (Auth): Duplicate user registration rejected (HTTP 400) — PASSED",
            "• TC-02 (Parsing): Invalid/corrupt file upload rejected (HTTP 400) — PASSED",
            "• TC-03 (RAG Retrieval): Top-3 context returned in 24.6ms (<= 100ms bound) — PASSED",
            "• TC-04 (Adaptive Escalation): Score >= 80% advances Bloom level (+1) — PASSED",
            "• TC-05 (Adaptive Remediation): Score < 50% regresses Bloom level (-1) — PASSED",
            "• TC-06 (Neural Voice): In-memory TTS byte stream generated in <= 1.2s — PASSED",
            "• TC-07 (Rubric Determinism): 5-factor scoring formula convergence — PASSED"
        ]
    )

    # Slide 11: Conclusion & Q&A
    s11 = prs.slides.add_slide(prs.slide_layouts[0])
    s11.shapes.title.text = "Conclusion & Q&A"
    s11.shapes.title.text_frame.paragraphs[0].font.size = Pt(36)
    s11.shapes.title.text_frame.paragraphs[0].font.bold = True
    s11.shapes.title.text_frame.paragraphs[0].font.color.rgb = RGBColor(26, 54, 93)
    
    sub11 = s11.placeholders[1]
    sub11.text = (
        "SmartInterview: Grounded, Adaptive, and Deterministic Technical Interview Preparation.\n\n"
        "Bridging higher education and industry hiring through 402-chunk RAG, Bloom's cognitive engine, and low-latency voice.\n\n"
        "Thank you! We invite questions from the panel."
    )
    for p in sub11.text_frame.paragraphs:
        p.font.size = Pt(18)

    output_path = os.path.join(OUT_DIR, 'SmartInterview_Presentation_Final.pptx')
    prs.save(output_path)
    print(f"Successfully generated clean widescreen {output_path} with 11 slides!")

if __name__ == "__main__":
    build_pptx()
