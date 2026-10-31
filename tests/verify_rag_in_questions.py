"""Verify RAG context is populated in actual interview questions."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
os.environ.setdefault("GROQ_API_KEY", "test")

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from app.database import SessionLocal
from app.models.question import InterviewQuestion
from app.models.interview import InterviewSession

db = SessionLocal()

# Get the most recent sessions
sessions = (
    db.query(InterviewSession)
    .order_by(InterviewSession.id.desc())
    .limit(3)
    .all()
)

print("=" * 70)
print("CHECKING RAG CONTEXT IN RECENT INTERVIEW QUESTIONS")
print("=" * 70)

for session in sessions:
    print(f"\n--- Session {session.id} (mode={session.mode}, status={session.status}) ---")
    
    questions = (
        db.query(InterviewQuestion)
        .filter(InterviewQuestion.session_id == session.id)
        .order_by(InterviewQuestion.question_number)
        .all()
    )
    
    for q in questions:
        print(f"\n  Q{q.question_number}: {q.question_text[:80]}...")
        print(f"  Skill: {q.skill}")
        print(f"  Difficulty: {q.difficulty}")
        
        # Check RAG context
        rag = q.rag_context
        if rag is None:
            print("  RAG Context: *** NONE - NOT POPULATED ***")
        elif isinstance(rag, list) and len(rag) == 0:
            print("  RAG Context: *** EMPTY LIST ***")
        elif isinstance(rag, list):
            print(f"  RAG Context: {len(rag)} chunks retrieved")
            for i, chunk in enumerate(rag):
                if isinstance(chunk, dict):
                    cid = chunk.get("chunk_id", "?")
                    domain = chunk.get("domain", "?")
                    concept = chunk.get("concept", "?")
                    text_len = len(chunk.get("text", ""))
                    score = chunk.get("score") or chunk.get("final_score") or "?"
                    sources = chunk.get("sources", "?")
                    print(f"    [{i+1}] chunk_id={cid}, domain={domain}, concept={concept}, text_len={text_len}, score={score}, sources={sources}")
                else:
                    print(f"    [{i+1}] {str(chunk)[:100]}")
        else:
            print(f"  RAG Context: (type={type(rag).__name__}) {str(rag)[:200]}")
        
        # Check retrieval mode used
        if hasattr(q, 'metadata') and q.metadata:
            rag_mode = None
            if isinstance(q.metadata, dict):
                rag_mode = q.metadata.get("rag_mode")
            print(f"  RAG Mode: {rag_mode or 'not recorded'}")

db.close()
print("\n" + "=" * 70)

