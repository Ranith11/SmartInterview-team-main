import sys
import os
from datetime import datetime, timezone, timedelta

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(REPO_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.database import SessionLocal
from app.models.user import User
from app.models.resume import Resume
from app.models.interview import InterviewSession
from app.models.question import InterviewQuestion, Answer, AnswerEvaluation
from app.services.auth_service import hash_password
from app.services.interview_service import get_weak_skill_profiles

def seed():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "weak_e2e@example.com").first()
        if not user:
            user = User(
                name="Weak E2E Candidate",
                email="weak_e2e@example.com",
                password_hash=hash_password("Password123!"),
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created user {user.id}: {user.email}")
        else:
            print(f"Found existing user {user.id}: {user.email}")

        # Check for resume
        resume = db.query(Resume).filter(Resume.user_id == user.id).first()
        if not resume:
            resume = Resume(
                user_id=user.id,
                filename="sample_resume.pdf",
                file_path="uploads/sample_resume.pdf",
                raw_text="Experienced engineer in Python and SQL databases.",
                skills=["Python", "SQL"],
            )
            db.add(resume)
            db.commit()
            db.refresh(resume)
            print(f"Created resume {resume.id}")

        # Check existing sessions
        sess_count = db.query(InterviewSession).filter(
            InterviewSession.user_id == user.id,
            InterviewSession.status == "completed"
        ).count()

        if sess_count < 2:
            now = datetime.now(timezone.utc)
            # Session 1: completed 2 days ago
            s1 = InterviewSession(
                user_id=user.id,
                resume_id=resume.id,
                difficulty="medium",
                question_type="mixed",
                question_count=2,
                selected_skills=["Python", "SQL"],
                status="completed",
                is_adaptive=True,
                mode="normal",
                started_at=now - timedelta(days=2),
                completed_at=now - timedelta(days=2),
            )
            db.add(s1)
            db.commit()
            db.refresh(s1)

            q1 = InterviewQuestion(session_id=s1.id, question_number=1, skill="Python", question_type="technical", difficulty="medium", question_text="Explain Python list comprehension", bloom_level="understand", bloom_level_number=2)
            q2 = InterviewQuestion(session_id=s1.id, question_number=2, skill="SQL", question_type="technical", difficulty="medium", question_text="Explain SQL indexing", bloom_level="understand", bloom_level_number=2)
            db.add_all([q1, q2])
            db.commit()

            a1 = Answer(session_id=s1.id, question_id=q1.id, user_id=user.id, answer_text="List comprehension creates lists concisely.")
            a2 = Answer(session_id=s1.id, question_id=q2.id, user_id=user.id, answer_text="Indexing speeds up select queries.")
            db.add_all([a1, a2])
            db.commit()

            ev1 = AnswerEvaluation(answer_id=a1.id, question_id=q1.id, technical_score=40, completeness_score=40, relevance_score=45, semantic_similarity_score=40, concept_coverage_score=45, overall_score=42.0, feedback="Basic answer, needs depth.")
            ev2 = AnswerEvaluation(answer_id=a2.id, question_id=q2.id, technical_score=35, completeness_score=35, relevance_score=38, semantic_similarity_score=35, concept_coverage_score=38, overall_score=36.0, feedback="Lacks B-Tree explanation.")
            db.add_all([ev1, ev2])
            db.commit()

            # Session 2: completed 1 day ago
            s2 = InterviewSession(
                user_id=user.id,
                resume_id=resume.id,
                difficulty="medium",
                question_type="mixed",
                question_count=2,
                selected_skills=["Python", "SQL"],
                status="completed",
                is_adaptive=True,
                mode="normal",
                started_at=now - timedelta(days=1),
                completed_at=now - timedelta(days=1),
            )
            db.add(s2)
            db.commit()
            db.refresh(s2)

            q3 = InterviewQuestion(session_id=s2.id, question_number=1, skill="Python", question_type="technical", difficulty="medium", question_text="Explain Python generators", bloom_level="apply", bloom_level_number=3)
            q4 = InterviewQuestion(session_id=s2.id, question_number=2, skill="SQL", question_type="technical", difficulty="medium", question_text="Explain SQL ACID properties", bloom_level="understand", bloom_level_number=2)
            db.add_all([q3, q4])
            db.commit()

            a3 = Answer(session_id=s2.id, question_id=q3.id, user_id=user.id, answer_text="Generators yield values one by one.")
            a4 = Answer(session_id=s2.id, question_id=q4.id, user_id=user.id, answer_text="ACID means atomicity, consistency, isolation, durability.")
            db.add_all([a3, a4])
            db.commit()

            ev3 = AnswerEvaluation(answer_id=a3.id, question_id=q3.id, technical_score=45, completeness_score=45, relevance_score=50, semantic_similarity_score=45, concept_coverage_score=50, overall_score=46.0, feedback="Needs memory comparison.")
            ev4 = AnswerEvaluation(answer_id=a4.id, question_id=q4.id, technical_score=40, completeness_score=40, relevance_score=40, semantic_similarity_score=40, concept_coverage_score=40, overall_score=40.0, feedback="Mention isolation levels.")
            db.add_all([ev3, ev4])
            db.commit()
            print("Seeded 2 completed sessions for weak_e2e user.")

        profiles = get_weak_skill_profiles(db, user.id)
        print("Weak Skill Profile Result:")
        print(profiles)
    finally:
        db.close()

if __name__ == "__main__":
    seed()
