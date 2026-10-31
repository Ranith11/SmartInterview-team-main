"""
SmartInterview — Remediation Service
Closed-Loop Adaptive Mastery Engine

This service powers the "Review Weak Areas & Retry" feature:
1. DIAGNOSIS: Analyses a completed session's per-skill scores to separate
   weak topics (< WEAK_THRESHOLD) from mastered topics (>= STRONG_THRESHOLD).
2. NOTES GENERATION: Generates AI-powered, mode-aware study notes:
   - Resume+JD mode → retrieves from original 'technical_kb' (402-chunk, 8-domain curated KB)
   - Syllabus mode  → retrieves from 'syllabus_kb' (candidate's own uploaded material)
   These collections are fully separate and never conflict.
3. SESSION SPAWNING: Creates a new focused interview session restricted
   to weak topics only, cloning the original session's resume/JD/syllabus context.

Edge cases handled:
- All topics mastered: returns empty weak list, suggests harder mode
- No evaluations yet: raises ValueError with clear message
- Syllabus mode with no syllabus_kb chunks for topic: falls back to LLM general knowledge
- Resume mode with no technical_kb match: falls back to LLM general knowledge
- Single-topic sessions: handles gracefully (1 weak or 1 strong topic)
- Remediation of a remediation session: allowed, always re-diagnoses fresh
"""

import chromadb
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session as DBSession

from app.config import CHROMA_DB_DIR
from app.models.interview import InterviewSession
from app.models.question import InterviewQuestion, Answer, AnswerEvaluation
from app.models.resume import Resume
from app.services.llm_client import get_universal_llm_client, get_universal_model_name

# ── Thresholds ────────────────────────────────────────────────────────────────
WEAK_THRESHOLD = 65      # Below this → weak, needs remediation
STRONG_THRESHOLD = 75    # At or above this → mastered, skipped in retry

# Collection names — these are separate, never conflict
COLLECTION_TECHNICAL_KB = "technical_kb"
COLLECTION_SYLLABUS_KB  = "syllabus_kb"

# Singleton embedding model (shared, lazy-initialized)
_embedding_model: SentenceTransformer | None = None


def _get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model


# ── 1. DIAGNOSIS ─────────────────────────────────────────────────────────────

def diagnose_session(db: DBSession, user_id: int, session_id: int) -> dict:
    """
    Analyse a completed session and classify each skill into:
    - weak_topics: skills where avg score < WEAK_THRESHOLD
    - strong_topics: skills where avg score >= STRONG_THRESHOLD
    - borderline_topics: scores between WEAK and STRONG thresholds
    - per_skill_details: full breakdown for UI display

    Edge cases:
    - No evaluations → raises ValueError
    - All topics mastered → weak_topics is empty, suggests harder mode
    - Only 1 question with no skill tag → uses 'General' as skill name
    """
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == user_id,
    ).first()
    if not session:
        raise ValueError("Interview session not found.")

    questions = (
        db.query(InterviewQuestion)
        .filter(InterviewQuestion.session_id == session_id)
        .order_by(InterviewQuestion.question_number)
        .all()
    )

    # Collect per-skill scores
    skill_data: dict[str, list[float]] = {}
    skill_feedback: dict[str, list[str]] = {}
    skill_weaknesses: dict[str, list[str]] = {}
    has_any_evaluation = False

    for q in questions:
        evaluation = db.query(AnswerEvaluation).filter(
            AnswerEvaluation.question_id == q.id
        ).first()
        if not evaluation:
            continue

        has_any_evaluation = True
        skill = q.skill or "General"

        skill_data.setdefault(skill, []).append(evaluation.overall_score)

        if evaluation.feedback:
            skill_feedback.setdefault(skill, []).append(evaluation.feedback)
        if evaluation.weaknesses:
            # weaknesses can be a list or a string
            w = evaluation.weaknesses
            if isinstance(w, list):
                skill_weaknesses.setdefault(skill, []).extend(w)
            elif isinstance(w, str) and w.strip():
                skill_weaknesses.setdefault(skill, []).append(w)

    if not has_any_evaluation:
        raise ValueError(
            "No evaluations found for this session. "
            "Please complete the interview fully before reviewing weak areas."
        )

    # Classify topics
    weak_topics: list[dict] = []
    strong_topics: list[dict] = []
    borderline_topics: list[dict] = []
    per_skill_details: dict = {}

    for skill, scores in skill_data.items():
        avg = round(sum(scores) / len(scores), 1)
        entry = {
            "skill": skill,
            "average_score": avg,
            "questions_count": len(scores),
            "weaknesses": skill_weaknesses.get(skill, []),
            "feedback_snippets": skill_feedback.get(skill, []),
        }
        per_skill_details[skill] = entry

        if avg < WEAK_THRESHOLD:
            weak_topics.append(entry)
        elif avg >= STRONG_THRESHOLD:
            strong_topics.append(entry)
        else:
            borderline_topics.append(entry)

    # Sort weak worst-first so most critical topic appears first in notes
    weak_topics.sort(key=lambda x: x["average_score"])

    all_mastered = len(weak_topics) == 0 and len(borderline_topics) == 0

    return {
        "session_id": session_id,
        "mode": session.mode,                   # "normal" or "syllabus"
        "syllabus_id": session.syllabus_id,
        "resume_id": session.resume_id,
        "weak_topics": weak_topics,
        "strong_topics": strong_topics,
        "borderline_topics": borderline_topics,
        "per_skill_details": per_skill_details,
        "all_mastered": all_mastered,
        "weak_count": len(weak_topics),
        "strong_count": len(strong_topics),
    }


# ── 2. NOTES GENERATION ───────────────────────────────────────────────────────

def _retrieve_rag_chunks(
    topics: list[str],
    collection_name: str,
    n_per_topic: int = 5,
    where_filter: dict | None = None,
) -> dict[str, list[str]]:
    """
    Query ChromaDB for the given topics from the specified collection.
    Returns a dict: {topic: [chunk_text, ...]}

    Uses the original verified collections only:
    - technical_kb  (Resume+JD mode) — 402 chunks, 8 domains, curated
    - syllabus_kb   (Syllabus mode)  — uploaded course material

    Falls back to empty list if collection or topic has no matching chunks.
    This is intentional: the notes generator will handle the empty case with
    a graceful LLM-only fallback.
    """
    try:
        client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
        try:
            collection = client.get_collection(name=collection_name)
        except Exception:
            return {t: [] for t in topics}

        model = _get_embedding_model()
        result: dict[str, list[str]] = {}

        for topic in topics:
            try:
                query_vec = model.encode([topic], convert_to_numpy=True).tolist()
                kwargs: dict = {
                    "query_embeddings": query_vec,
                    "n_results": min(n_per_topic, collection.count()),
                    "include": ["documents"],
                }
                if where_filter:
                    kwargs["where"] = where_filter

                res = collection.query(**kwargs)
                docs = res.get("documents", [[]])[0] or []
                result[topic] = [d for d in docs if d and d.strip()]
            except Exception as e:
                print(f"[RemediationService] RAG query failed for topic '{topic}' "
                      f"in '{collection_name}': {e}")
                result[topic] = []

        return result

    except Exception as e:
        print(f"[RemediationService] ChromaDB connection failed: {e}")
        return {t: [] for t in topics}


def _build_notes_prompt(
    weak_topics: list[dict],
    rag_context: dict[str, list[str]],
    mode: str,
    source_label: str,
) -> str:
    """
    Build the Groq prompt for generating structured study notes.
    Incorporates:
    - RAG context from the appropriate verified collection
    - Per-skill weakness analysis from evaluation feedback
    - Candidate's score context for personalised guidance
    """
    sections = []

    for topic_data in weak_topics:
        skill = topic_data["skill"]
        score = topic_data["average_score"]
        weaknesses = topic_data.get("weaknesses", [])
        feedback = topic_data.get("feedback_snippets", [])
        chunks = rag_context.get(skill, [])

        section = f"## Topic: {skill} (Your Score: {score}%)\n\n"

        if weaknesses:
            section += "### ⚠️ Where You Lost Marks\n"
            for w in weaknesses[:3]:
                section += f"- {w}\n"
            section += "\n"

        if chunks:
            context_text = "\n\n".join(chunks[:4])
            section += (
                f"### 📚 Relevant Knowledge ({source_label})\n"
                f"Use the following verified reference material to generate concise, "
                f"accurate, high-yield revision notes:\n\n"
                f"```\n{context_text[:2000]}\n```\n\n"
            )
        else:
            section += (
                f"### 📚 Knowledge Source\n"
                f"No specific {source_label} chunks matched this topic. "
                f"Generate authoritative notes from your general knowledge.\n\n"
            )

        sections.append(section)

    combined = "\n---\n".join(sections)
    mode_instruction = (
        "Focus on university exam and coursework topics based on the provided syllabus context."
        if mode == "syllabus"
        else "Focus on technical interview readiness, system design implications, and production best practices."
    )

    prompt = f"""You are an expert AI tutor generating personalised revision notes for a student who just completed a mock technical interview.

The student struggled with the following topics. Generate structured, high-yield study notes for EACH topic.

{combined}

---

**Instructions:**
- {mode_instruction}
- For each topic, provide:
  1. **🎯 Core Concept**: Concise, accurate definition (2-3 sentences max)
  2. **⚠️ Where candidates typically lose marks**: Key pitfalls and misconceptions
  3. **💡 Key Points to Remember**: 4-6 bullet points, fact-dense, exam-ready
  4. **💻 Code / Formula / Example** (if applicable): The gold-standard implementation
  5. **🔥 Common Interview Traps**: Edge cases the interviewer might probe
- Use Markdown formatting with headers, bullet points, and code blocks.
- Be specific, not generic. Every sentence must add value.
- Do NOT include introductory fluff. Start immediately with the first topic header.
- Total length: 400-800 words across all topics.
"""
    return prompt


def generate_remediation_notes(
    db: DBSession, user_id: int, session_id: int
) -> dict:
    """
    Main entry point: generates mode-aware AI study notes for weak topics.

    Flow:
    1. Diagnose the session → get weak topics with evaluation context
    2. Query the correct ChromaDB collection based on session mode:
       - "normal" → technical_kb (original curated 402-chunk, 8-domain KB)
       - "syllabus" → syllabus_kb (candidate's own uploaded course material)
    3. Build a Groq prompt enriched with RAG context + weakness analysis
    4. Return structured notes + metadata for frontend rendering

    Edge cases:
    - All mastered → returns `all_mastered: True`, notes are empty, button changes
    - No evaluations → raises ValueError
    - Empty RAG results for a topic → falls back to LLM general knowledge
    - Groq failure → raises RuntimeError with actionable message
    """
    # Step 1: Diagnose
    diagnosis = diagnose_session(db, user_id, session_id)

    if diagnosis["all_mastered"]:
        return {
            "session_id": session_id,
            "all_mastered": True,
            "weak_topics": [],
            "strong_topics": diagnosis["strong_topics"],
            "notes_markdown": "",
            "source": "N/A",
            "mode": diagnosis["mode"],
        }

    weak_topics = diagnosis["weak_topics"]

    # Also include borderline topics in notes (they need attention too)
    # but the retry session only targets genuinely weak topics
    topics_for_notes = weak_topics + diagnosis["borderline_topics"]
    topic_names = [t["skill"] for t in topics_for_notes]

    # Step 2: RAG retrieval from the correct verified collection
    mode = diagnosis["mode"]

    if mode == "syllabus":
        collection_name = COLLECTION_SYLLABUS_KB
        source_label = "your uploaded syllabus"
    else:
        # Resume+JD mode — use the original curated technical_kb ONLY
        collection_name = COLLECTION_TECHNICAL_KB
        source_label = "SmartInterview Technical Knowledge Base"

    rag_context = _retrieve_rag_chunks(
        topics=topic_names,
        collection_name=collection_name,
    )

    # Step 3: Generate notes via Groq
    prompt = _build_notes_prompt(
        weak_topics=topics_for_notes,
        rag_context=rag_context,
        mode=mode,
        source_label=source_label,
    )

    try:
        client = get_universal_llm_client()
        model = get_universal_model_name()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior technical educator and interview coach. "
                        "Generate precise, structured, high-yield revision notes. "
                        "Every line must be factually correct and immediately useful."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=1800,
        )
        notes_markdown = response.choices[0].message.content.strip()
    except Exception as e:
        raise RuntimeError(
            f"Failed to generate study notes via AI engine: {str(e)}. "
            "Please ensure the backend is connected to Groq and try again."
        )

    return {
        "session_id": session_id,
        "mode": mode,
        "all_mastered": False,
        "weak_topics": [t["skill"] for t in weak_topics],
        "borderline_topics": [t["skill"] for t in diagnosis["borderline_topics"]],
        "strong_topics": [t["skill"] for t in diagnosis["strong_topics"]],
        "weak_topic_details": topics_for_notes,
        "notes_markdown": notes_markdown,
        "source": source_label,
        "collection_used": collection_name,
        "rag_chunks_found": {k: len(v) for k, v in rag_context.items()},
    }


# ── 3. SESSION SPAWNER ────────────────────────────────────────────────────────

def start_remediation_session(
    db: DBSession, user_id: int, source_session_id: int
) -> dict:
    """
    Create a new focused interview session targeting ONLY the weak topics
    from a previous session. Clones resume/JD/syllabus context automatically.

    Edge cases:
    - All topics mastered → raises ValueError with clear message
    - No evaluations → raises ValueError
    - Syllabus mode with expired temp collection → uses syllabus_kb chunks
    - Remediation of a remediation → allowed, always re-diagnoses fresh

    Returns the standard AdaptiveStartResponse dict from create_interview_session.
    """
    diagnosis = diagnose_session(db, user_id, source_session_id)

    if diagnosis["all_mastered"]:
        raise ValueError(
            "All topics were mastered in this session (≥ 75% on every skill). "
            "Try a harder difficulty level instead of a remediation session."
        )

    if not diagnosis["weak_topics"]:
        raise ValueError(
            "No weak topics detected. Only borderline topics exist. "
            "Consider practicing these: "
            + ", ".join(t["skill"] for t in diagnosis["borderline_topics"])
        )

    # Get source session for context cloning
    source = db.query(InterviewSession).filter(
        InterviewSession.id == source_session_id,
        InterviewSession.user_id == user_id,
    ).first()

    weak_skill_names = [t["skill"] for t in diagnosis["weak_topics"]]
    # Include borderline topics in the retry session too
    retry_skills = weak_skill_names + [
        t["skill"] for t in diagnosis["borderline_topics"]
    ]

    # Import here to avoid circular imports
    from app.services.interview_service import create_interview_session

    if source.mode == "syllabus":
        # Syllabus mode: restart with same syllabus, filtered to weak topics only
        if not source.syllabus_id:
            raise ValueError(
                "Original session had syllabus mode but no syllabus_id. Cannot clone."
            )
        result = create_interview_session(
            db=db,
            user_id=user_id,
            resume_id=source.resume_id,
            difficulty=source.difficulty,
            question_type=source.question_type,
            question_count=None,         # adaptive — runs until mastery
            selected_skills=retry_skills,
            mode="syllabus",
            syllabus_id=source.syllabus_id,
            selected_topics=retry_skills,
        )
    else:
        # Normal mode: restart with same resume, targeted skills
        result = create_interview_session(
            db=db,
            user_id=user_id,
            resume_id=source.resume_id,
            difficulty=source.difficulty,
            question_type=source.question_type,
            question_count=None,         # adaptive — runs until mastery
            selected_skills=retry_skills,
            mode="normal",
        )

    # Tag the new session so the UI can show "🎯 Focused Retest" badge
    new_session: InterviewSession = result["session"]
    state = new_session.adaptive_state or {}
    if isinstance(state, dict):
        state["is_remediation"] = True
        state["source_session_id"] = source_session_id
        state["targeted_skills"] = retry_skills
        new_session.adaptive_state = state
        db.commit()
        db.refresh(new_session)

    return {
        **result,
        "is_remediation": True,
        "targeted_skills": retry_skills,
        "source_session_id": source_session_id,
    }
