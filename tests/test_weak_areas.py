"""
SmartInterview — Weak Areas Targeted Practice Test Suite
Tests:
  - Weak skill profile calculation & classification
  - Insufficient evidence protection
  - Confidence & trend detection
  - Baseline snapshot preservation
  - Targeted interview creation in weak_areas mode
  - Deterministic Bloom taxonomy starting point
  - Skill movement comparison (improved, declined, stable, baseline_unavailable)
  - Edge cases (no history, zero weak areas, ties, unsupported retrieval)
  - FastAPI endpoints (/api/users/weak-skills, /api/interviews/start, /api/interviews/{id}/comparison)
"""

import sys
import os
from datetime import datetime, timezone
from unittest.mock import patch

# Ensure backend is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(REPO_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.models.user import User
from app.models.resume import Resume
from app.models.job_description import JobDescription
from app.models.interview import InterviewSession
from app.models.question import InterviewQuestion, Answer, AnswerEvaluation
from app.services.interview_service import (
    get_weak_skill_profiles,
    get_user_performance,
    _build_baselines_snapshot,
    create_interview_session,
    get_skill_comparison,
    WEAK_THRESHOLD,
    NEEDS_PRACTICE_THRESHOLD,
    STRONG_THRESHOLD,
    MIN_ASSESSMENTS_FOR_WEAK,
    STABLE_TOLERANCE,
)
from app.main import app
from app.services.auth_service import create_access_token


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh in-memory SQLite database for each test function."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_user(test_db):
    user = User(
        name="Test Candidate",
        email="candidate@example.com",
        password_hash="fakehash123",
        created_at=datetime.now(timezone.utc),
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


def _create_completed_session_with_evals(test_db, user_id, evaluations_data, mode="normal"):
    """
    Helper to seed a completed adaptive session.
    evaluations_data: list of dicts: {"skill": str, "overall_score": float, "question_text": str}
    """
    session = InterviewSession(
        user_id=user_id,
        difficulty="medium",
        question_type="mixed",
        question_count=len(evaluations_data),
        selected_skills=list({d["skill"] for d in evaluations_data}),
        status="completed",
        is_adaptive=True,
        mode=mode,
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
    )
    test_db.add(session)
    test_db.commit()
    test_db.refresh(session)

    for idx, ed in enumerate(evaluations_data, start=1):
        q = InterviewQuestion(
            session_id=session.id,
            question_number=idx,
            skill=ed["skill"],
            question_type="practical",
            difficulty="medium",
            question_text=ed.get("question_text", f"Question about {ed['skill']}"),
            bloom_level="remember",
            bloom_level_number=1,
        )
        test_db.add(q)
        test_db.commit()
        test_db.refresh(q)

        ans = Answer(
            session_id=session.id,
            user_id=user_id,
            question_id=q.id,
            answer_text="Test candidate answer text",
            submitted_at=datetime.now(timezone.utc),
        )
        test_db.add(ans)
        test_db.commit()
        test_db.refresh(ans)

        eval_rec = AnswerEvaluation(
            question_id=q.id,
            answer_id=ans.id,
            technical_score=ed["overall_score"],
            completeness_score=ed["overall_score"],
            relevance_score=ed["overall_score"],
            semantic_similarity_score=ed["overall_score"],
            concept_coverage_score=ed["overall_score"],
            overall_score=ed["overall_score"],
            feedback="Good effort",
            strengths=["basics"],
            weaknesses=["edge cases"],
            evaluated_at=datetime.now(timezone.utc),
        )
        test_db.add(eval_rec)
        test_db.commit()

    return session


# ── TEST SUITE ─────────────────────────────────────────────────────────────

def test_weak_skill_profiles_no_history(test_db, test_user):
    """Zero completed sessions returns has_data=False and empty lists."""
    profiles = get_weak_skill_profiles(test_db, test_user.id)
    assert profiles["has_data"] is False
    assert profiles["weak_skills"] == []
    assert profiles["all_assessed_skills"] == []
    assert profiles["total_completed_sessions"] == 0


def test_weak_skill_profiles_classification_and_insufficient_evidence(test_db, test_user):
    """
    Test classification thresholds:
    - Score < 50 with >= 2 evals -> 'weak'
    - Score 50-64 with >= 2 evals -> 'needs_practice'
    - Score >= 75 with >= 2 evals -> 'strong'
    - Score < 50 with only 1 eval -> 'insufficient_data' (insufficient evidence protection!)
    """
    evals_session1 = [
        {"skill": "Python", "overall_score": 40.0},
        {"skill": "Docker", "overall_score": 60.0},
        {"skill": "Kubernetes", "overall_score": 35.0}, # only 1 eval total
        {"skill": "SQL", "overall_score": 85.0},
    ]
    evals_session2 = [
        {"skill": "Python", "overall_score": 44.0}, # Python avg = 42.0 (< 50, count 2) -> weak
        {"skill": "Docker", "overall_score": 58.0}, # Docker avg = 59.0 (50-64, count 2) -> needs_practice
        {"skill": "SQL", "overall_score": 95.0},    # SQL avg = 90.0 (>= 75, count 2) -> strong
    ]

    _create_completed_session_with_evals(test_db, test_user.id, evals_session1)
    _create_completed_session_with_evals(test_db, test_user.id, evals_session2)

    profiles = get_weak_skill_profiles(test_db, test_user.id)
    assert profiles["has_data"] is True
    assert profiles["total_completed_sessions"] == 2

    all_skills_map = {p["skill"]: p for p in profiles["all_assessed_skills"]}

    # Python: count=2, avg=42.0 -> weak
    assert all_skills_map["Python"]["classification"] == "weak"
    assert all_skills_map["Python"]["average_score"] == 42.0
    assert all_skills_map["Python"]["assessment_count"] == 2

    # Docker: count=2, avg=59.0 -> needs_practice
    assert all_skills_map["Docker"]["classification"] == "needs_practice"
    assert all_skills_map["Docker"]["average_score"] == 59.0

    # SQL: count=2, avg=90.0 -> strong
    assert all_skills_map["SQL"]["classification"] == "strong"
    assert all_skills_map["SQL"]["average_score"] == 90.0

    # Kubernetes: only 1 eval -> insufficient_data, NOT labeled as weak!
    assert all_skills_map["Kubernetes"]["assessment_count"] == 1
    assert all_skills_map["Kubernetes"]["classification"] == "insufficient_data"

    # Weak skills list should contain Python and Docker, weakest first
    weak_skill_names = [p["skill"] for p in profiles["weak_skills"]]
    assert weak_skill_names == ["Python", "Docker"]


def test_weak_skill_profiles_confidence_and_trend(test_db, test_user):
    """
    Test confidence levels and trend calculation:
    - Count < 3 -> low confidence
    - Count 3-5 -> medium confidence
    - Count > 5 -> high confidence
    - Score improving by > STABLE_TOLERANCE -> trend 'improving'
    """
    # 6 evals for System Design: older avg = 30, newer avg = 80 -> improving trend
    evals = [
        {"skill": "System Design", "overall_score": 25.0},
        {"skill": "System Design", "overall_score": 30.0},
        {"skill": "System Design", "overall_score": 35.0},
        {"skill": "System Design", "overall_score": 75.0},
        {"skill": "System Design", "overall_score": 80.0},
        {"skill": "System Design", "overall_score": 85.0},
    ]
    _create_completed_session_with_evals(test_db, test_user.id, evals)

    profiles = get_weak_skill_profiles(test_db, test_user.id)
    sd = profiles["all_assessed_skills"][0]
    assert sd["skill"] == "System Design"
    assert sd["assessment_count"] == 6
    assert sd["confidence"] == "high"
    assert sd["trend"] == "improving"


def test_baselines_snapshot_immutability(test_db, test_user):
    """
    Test that _build_baselines_snapshot captures the historical average accurately
    and is snapshotted so later sessions do not modify the saved snapshot.
    """
    evals = [
        {"skill": "Python", "overall_score": 40.0},
        {"skill": "Python", "overall_score": 50.0},
    ]
    _create_completed_session_with_evals(test_db, test_user.id, evals)

    snapshot = _build_baselines_snapshot(test_db, test_user.id, ["Python"])
    assert "python" in snapshot
    assert snapshot["python"]["average_score"] == 45.0
    assert snapshot["python"]["count"] == 2

    # Now add another session with a 90 score
    _create_completed_session_with_evals(test_db, test_user.id, [{"skill": "Python", "overall_score": 90.0}])

    # The snapshot taken earlier remains 45.0!
    assert snapshot["python"]["average_score"] == 45.0


@patch("app.services.interview_service.generate_single_question")
def test_create_interview_session_weak_areas_mode(mock_gen_q, test_db, test_user):
    """
    Test creating an interview session in weak_areas mode:
    - Mode is 'weak_areas'
    - Selected skills snapshot baselines
    - Difficulty is respected ('hard')
    - Does NOT require a Job Description
    - Bloom level starts at Remember
    """
    # Seed historical session so weak skills exist
    _create_completed_session_with_evals(test_db, test_user.id, [
        {"skill": "Python", "overall_score": 40.0},
        {"skill": "Python", "overall_score": 44.0},
        {"skill": "Docker", "overall_score": 55.0},
        {"skill": "Docker", "overall_score": 60.0},
    ])

    mock_gen_q.return_value = {
        "skill": "Python",
        "difficulty": "hard",
        "question_type": "mixed",
        "question_text": "What is Python GIL?",
        "bloom_level": "remember",
        "bloom_level_number": 1,
        "rag_context": [{"chunk_id": "c1", "text": "Python GIL docs"}],
        "rag_context_full": None,
    }

    result = create_interview_session(
        db=test_db,
        user_id=test_user.id,
        difficulty="hard",
        question_type="mixed",
        selected_skills=["Python", "Docker"],
        mode="weak_areas",
    )

    session = result["session"]
    question = result["current_question"]

    assert session.mode == "weak_areas"
    assert session.difficulty == "hard"
    assert session.selected_skills == ["Python", "Docker"]
    assert session.current_bloom_level == "remember"
    assert session.weak_area_baselines is not None
    assert "python" in session.weak_area_baselines
    assert session.weak_area_baselines["python"]["average_score"] == 42.0

    assert question.skill == "Python"
    assert question.question_number == 1
    assert question.bloom_level_number == 1


def test_create_interview_session_weak_areas_no_history_error(test_db, test_user):
    """Creating a weak_areas interview with no history and no skills raises clear ValueError."""
    with pytest.raises(ValueError) as excinfo:
        create_interview_session(
            db=test_db,
            user_id=test_user.id,
            mode="weak_areas",
        )
    assert "No weak areas identified" in str(excinfo.value)


def test_skill_comparison_movement(test_db, test_user):
    """
    Test get_skill_comparison correctly calculates before/after movement:
    - Improved (+30 points) -> 'improved'
    - Declined (-15 points) -> 'declined'
    - Stable (within +/- 3 points) -> 'stable'
    - Not in historical baseline -> 'baseline_unavailable'
    - Current session never included in baseline!
    """
    # 1. Historical baseline session
    _create_completed_session_with_evals(test_db, test_user.id, [
        {"skill": "Python", "overall_score": 40.0},
        {"skill": "Docker", "overall_score": 65.0},
        {"skill": "Go", "overall_score": 50.0},
    ])

    # 2. Targeted follow-up session with snapshotted baselines
    snapshot = {
        "python": {"display_name": "Python", "average_score": 40.0, "count": 1},
        "docker": {"display_name": "Docker", "average_score": 65.0, "count": 1},
        "go": {"display_name": "Go", "average_score": 50.0, "count": 1},
    }

    session = InterviewSession(
        user_id=test_user.id,
        difficulty="medium",
        question_type="mixed",
        question_count=4,
        selected_skills=["Python", "Docker", "Go", "Rust"],
        status="completed",
        is_adaptive=True,
        mode="weak_areas",
        weak_area_baselines=snapshot,
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
    )
    test_db.add(session)
    test_db.commit()
    test_db.refresh(session)

    # Add evaluated answers in this targeted session:
    # Python: 75 (+35 -> improved)
    # Docker: 50 (-15 -> declined)
    # Go: 51 (+1 -> stable within +/- 3)
    # Rust: 80 (not in baseline -> baseline_unavailable)
    eval_specs = [
        ("Python", 75.0),
        ("Docker", 50.0),
        ("Go", 51.0),
        ("Rust", 80.0),
    ]
    for idx, (sk, score) in enumerate(eval_specs, start=1):
        q = InterviewQuestion(
            session_id=session.id,
            question_number=idx,
            skill=sk,
            question_type="practical",
            difficulty="medium",
            question_text=f"Q about {sk}",
        )
        test_db.add(q)
        test_db.commit()
        test_db.refresh(q)

        ans = Answer(session_id=session.id, user_id=test_user.id, question_id=q.id, answer_text="Ans")
        test_db.add(ans)
        test_db.commit()
        test_db.refresh(ans)

        ev = AnswerEvaluation(
            question_id=q.id,
            answer_id=ans.id,
            technical_score=score,
            completeness_score=score,
            relevance_score=score,
            semantic_similarity_score=score,
            concept_coverage_score=score,
            overall_score=score,
            feedback="Eval feedback",
        )
        test_db.add(ev)
        test_db.commit()

    comparison = get_skill_comparison(test_db, session)
    cmap = {c["skill"]: c for c in comparison}

    assert cmap["Python"]["status"] == "improved"
    assert cmap["Python"]["previous_score"] == 40.0
    assert cmap["Python"]["current_score"] == 75.0
    assert cmap["Python"]["change"] == 35.0

    assert cmap["Docker"]["status"] == "declined"
    assert cmap["Docker"]["previous_score"] == 65.0
    assert cmap["Docker"]["current_score"] == 50.0
    assert cmap["Docker"]["change"] == -15.0

    assert cmap["Go"]["status"] == "stable"
    assert cmap["Go"]["previous_score"] == 50.0
    assert cmap["Go"]["current_score"] == 51.0
    assert cmap["Go"]["change"] == 1.0

    assert cmap["Rust"]["status"] == "baseline_unavailable"
    assert cmap["Rust"]["previous_score"] is None
    assert cmap["Rust"]["current_score"] == 80.0
    assert cmap["Rust"]["change"] is None


def test_api_endpoints_integration(test_db, test_user):
    """
    Test FastAPI endpoints using TestClient:
    - GET /api/users/weak-skills
    - GET /api/interviews/{id}/comparison
    - GET /api/interviews/history includes mode
    """
    # Seed data
    sess = _create_completed_session_with_evals(test_db, test_user.id, [
        {"skill": "Python", "overall_score": 42.0},
        {"skill": "Python", "overall_score": 46.0},
    ], mode="weak_areas")

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    token = create_access_token(user_id=test_user.id)
    headers = {"Authorization": f"Bearer {token}"}

    client = TestClient(app)

    # 1. Test GET /api/users/weak-skills
    res = client.get("/api/users/weak-skills", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["has_data"] is True
    assert len(data["weak_skills"]) == 1
    assert data["weak_skills"][0]["skill"] == "Python"
    assert data["weak_skills"][0]["classification"] == "weak"

    # 2. Test GET /api/interviews/{id}/comparison
    res = client.get(f"/api/interviews/{sess.id}/comparison", headers=headers)
    assert res.status_code == 200
    comp_list = res.json()
    assert isinstance(comp_list, list)

    # 3. Test GET /api/interviews/history
    res = client.get("/api/interviews/history", headers=headers)
    assert res.status_code == 200
    hist = res.json()
    assert len(hist) >= 1
    assert hist[0]["mode"] == "weak_areas"

    # 4. Test POST /api/interviews/start with omitted difficulty and question_type
    with patch("app.services.interview_service.generate_single_question") as mock_gen_q:
        mock_gen_q.return_value = {
            "skill": "Python",
            "difficulty": "medium",
            "question_type": "mixed",
            "question_text": "Explain Python lists",
            "bloom_level": "remember",
            "bloom_level_number": 1,
            "rag_context": [],
            "rag_context_full": None,
        }
        start_res = client.post(
            "/api/interviews/start",
            headers=headers,
            json={
                "mode": "weak_areas",
                "selected_skills": ["Python"],
            },
        )
        assert start_res.status_code == 201
        start_data = start_res.json()
        assert start_data["mode"] == "weak_areas"
        assert start_data["difficulty"] == "medium"
        assert start_data["question_type"] == "mixed"
        assert start_data["current_bloom_level"] == "remember"
        assert start_data["current_question"]["difficulty"] == "medium"
        assert start_data["current_question"]["bloom_level"] == "remember"
        assert start_data["current_question"]["bloom_level_number"] == 1

    app.dependency_overrides.clear()


@patch("app.services.interview_service.generate_single_question")
def test_weak_areas_omitted_defaults_medium_and_bloom_remember(mock_gen_q, test_db, test_user):
    """
    Verify fixed default configuration when candidate starts weak-area interview:
    - Omitted difficulty defaults strictly to 'medium'
    - Omitted question_type defaults strictly to 'mixed'
    - Starting Bloom's level is Remember (Level 1)
    - Session has mode 'weak_areas'
    """
    _create_completed_session_with_evals(test_db, test_user.id, [
        {"skill": "Python", "overall_score": 40.0},
        {"skill": "Python", "overall_score": 45.0},
    ])

    mock_gen_q.return_value = {
        "skill": "Python",
        "difficulty": "medium",
        "question_type": "mixed",
        "question_text": "What is Python list comprehension?",
        "bloom_level": "remember",
        "bloom_level_number": 1,
        "rag_context": [],
        "rag_context_full": None,
    }

    # Call without difficulty or question_type arguments
    res = create_interview_session(
        db=test_db,
        user_id=test_user.id,
        selected_skills=["Python"],
        mode="weak_areas",
    )

    sess = res["session"]
    q = res["current_question"]

    assert sess.mode == "weak_areas"
    assert sess.difficulty == "medium"
    assert sess.question_type == "mixed"
    assert sess.current_bloom_level == "remember"
    assert q.difficulty == "medium"
    assert q.bloom_level == "remember"
    assert q.bloom_level_number == 1


@patch("app.services.interview_service.generate_single_question")
def test_zero_weak_areas_fallback_to_assessed_skills(mock_gen_q, test_db, test_user):
    """
    Edge case: Candidate has evaluated sessions, but ALL skills are strong (>75).
    weak_skills is empty, but create_interview_session(..., mode='weak_areas')
    falls back cleanly to all_assessed_skills sorted weakest first, rather than crashing.
    """
    _create_completed_session_with_evals(test_db, test_user.id, [
        {"skill": "TypeScript", "overall_score": 85.0},
        {"skill": "TypeScript", "overall_score": 85.0},
        {"skill": "Go", "overall_score": 95.0},
        {"skill": "Go", "overall_score": 95.0},
    ])

    profiles = get_weak_skill_profiles(test_db, test_user.id)
    assert profiles["has_data"] is True
    assert profiles["weak_skills"] == [] # zero weak areas!
    assert len(profiles["all_assessed_skills"]) == 2

    mock_gen_q.return_value = {
        "skill": "TypeScript",
        "difficulty": "medium",
        "question_type": "mixed",
        "question_text": "Explain TypeScript generics",
        "bloom_level": "remember",
        "bloom_level_number": 1,
        "rag_context": [],
        "rag_context_full": None,
    }

    # Should succeed without error, picking TypeScript first (85 < 95)
    res = create_interview_session(
        db=test_db,
        user_id=test_user.id,
        mode="weak_areas",
    )
    assert res["session"].mode == "weak_areas"
    assert res["session"].selected_skills[0] == "TypeScript"
    assert res["current_question"].skill == "TypeScript"


def test_score_ties_handling(test_db, test_user):
    """
    Edge case: Multiple weak skills with identical average scores.
    Profile aggregation and sorting cleanly handles ties deterministically.
    """
    _create_completed_session_with_evals(test_db, test_user.id, [
        {"skill": "SkillA", "overall_score": 40.0},
        {"skill": "SkillA", "overall_score": 40.0},
        {"skill": "SkillB", "overall_score": 40.0},
        {"skill": "SkillB", "overall_score": 40.0},
    ])

    profiles = get_weak_skill_profiles(test_db, test_user.id)
    assert len(profiles["weak_skills"]) == 2
    assert profiles["weak_skills"][0]["average_score"] == 40.0
    assert profiles["weak_skills"][1]["average_score"] == 40.0


def test_user_isolation_and_unauthorized_access(test_db, test_user):
    """
    Security & User Isolation:
    - User A's weak skills and comparison baselines cannot be accessed by User B.
    - Unauthenticated requests return 401 Unauthorized.
    """
    # Create second user
    user_b = User(
        name="User B",
        email="user_b@example.com",
        password_hash="fakehashB",
        created_at=datetime.now(timezone.utc),
    )
    test_db.add(user_b)
    test_db.commit()
    test_db.refresh(user_b)

    # Seed User A weak history
    _create_completed_session_with_evals(test_db, test_user.id, [
        {"skill": "UserASkill", "overall_score": 30.0},
        {"skill": "UserASkill", "overall_score": 35.0},
    ])

    # Seed User B strong history
    _create_completed_session_with_evals(test_db, user_b.id, [
        {"skill": "UserBSkill", "overall_score": 90.0},
        {"skill": "UserBSkill", "overall_score": 95.0},
    ])

    # Create weak_areas session for User A
    with patch("app.services.interview_service.generate_single_question") as mock_gen:
        mock_gen.return_value = {
            "skill": "UserASkill",
            "difficulty": "medium",
            "question_type": "mixed",
            "question_text": "Sample Q",
            "bloom_level": "remember",
            "bloom_level_number": 1,
            "rag_context": [],
            "rag_context_full": None,
        }
        user_a_sess = create_interview_session(
            db=test_db,
            user_id=test_user.id,
            mode="weak_areas",
            selected_skills=["UserASkill"],
        )["session"]

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    token_a = create_access_token(user_id=test_user.id)
    token_b = create_access_token(user_id=user_b.id)
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 1. Unauthenticated checks -> 401 or 403 (HTTPBearer without credentials returns 403)
    assert client.get("/api/users/weak-skills").status_code in (401, 403)
    assert client.get(f"/api/interviews/{user_a_sess.id}/comparison").status_code in (401, 403)
    assert client.post("/api/interviews/start", json={"difficulty": "medium"}).status_code in (401, 403)

    # 2. User B weak-skills does NOT see User A's skills
    res_b = client.get("/api/users/weak-skills", headers=headers_b)
    assert res_b.status_code == 200
    b_data = res_b.json()
    assert all(s["skill"] != "UserASkill" for s in b_data.get("weak_skills", []))

    # 3. User B cannot access User A's session comparison -> 404 Not Found (or 403 Forbidden)
    res_b_comp = client.get(f"/api/interviews/{user_a_sess.id}/comparison", headers=headers_b)
    assert res_b_comp.status_code in (403, 404)

    # 4. User A CAN access their own session comparison -> 200 OK
    res_a_comp = client.get(f"/api/interviews/{user_a_sess.id}/comparison", headers=headers_a)
    assert res_a_comp.status_code == 200

    app.dependency_overrides.clear()


@patch("app.services.interview_service.generate_syllabus_question")
@patch("app.services.interview_service.generate_single_question")
def test_normal_and_syllabus_modes_regression(mock_gen_q, mock_gen_syl, test_db, test_user):
    """
    Regression verification:
    - Normal interview mode creation continues working as expected without baselines.
    - Syllabus interview mode creation continues working as expected without baselines.
    """
    mock_gen_q.return_value = {
        "skill": "Python",
        "difficulty": "medium",
        "question_type": "mixed",
        "question_text": "Normal python question",
        "bloom_level": "remember",
        "bloom_level_number": 1,
        "rag_context": [],
        "rag_context_full": None,
    }
    mock_gen_syl.return_value = {
        "skill": "Trees",
        "difficulty": "hard",
        "question_type": "mixed",
        "question_text": "Explain binary search trees",
        "bloom_level": "remember",
        "bloom_level_number": 1,
        "rag_context": [],
        "rag_context_full": None,
    }

    # Add mock resume and JD for normal mode
    resume = Resume(
        user_id=test_user.id,
        filename="resume.pdf",
        file_path="resume.pdf",
        raw_text="Experienced Python Developer",
        skills=["Python"],
    )
    test_db.add(resume)
    jd = JobDescription(
        user_id=test_user.id,
        filename="jd.pdf",
        file_path="jd.pdf",
        raw_text="Python Developer Wanted",
        skills=["Python"],
    )
    test_db.add(jd)
    test_db.commit()
    test_db.refresh(resume)
    test_db.refresh(jd)

    # 1. Normal Mode
    normal_res = create_interview_session(
        db=test_db,
        user_id=test_user.id,
        resume_id=resume.id,
        difficulty="medium",
        question_type="mixed",
        question_count=5,
        mode="normal",
        selected_skills=["Python"],
    )
    assert normal_res["session"].mode == "normal"
    assert normal_res["session"].weak_area_baselines is None
    assert normal_res["current_question"].question_text == "Normal python question"

    # 2. Syllabus Mode
    syllabus_res = create_interview_session(
        db=test_db,
        user_id=test_user.id,
        difficulty="hard",
        question_type="mixed",
        question_count=10,
        mode="syllabus",
        selected_topics=["Trees", "Graphs"],
        syllabus_id="mock_syllabus_uuid",
    )
    assert syllabus_res["session"].mode == "syllabus"
    assert syllabus_res["session"].syllabus_id == "mock_syllabus_uuid"
    assert syllabus_res["session"].weak_area_baselines is None


def test_unassessed_questions_not_treated_as_zero(test_db, test_user):
    """
    Verification:
    If a question is asked but no Answer/Evaluation is submitted,
    the score calculation ignores it rather than treating it as 0.0.
    """
    sess = InterviewSession(
        user_id=test_user.id,
        difficulty="medium",
        question_type="mixed",
        question_count=5,
        selected_skills=["FastAPI"],
        status="in_progress",
        is_adaptive=True,
        mode="weak_areas",
        weak_area_baselines={"fastapi": {"display_name": "FastAPI", "average_score": 45.0, "count": 2}},
        started_at=datetime.now(timezone.utc),
    )
    test_db.add(sess)
    test_db.commit()

    # Question 1: Evaluated at 80.0
    q1 = InterviewQuestion(
        session_id=sess.id,
        question_text="Q1 text",
        question_type="mixed",
        difficulty="medium",
        skill="FastAPI",
        bloom_level="remember",
        bloom_level_number=1,
        question_number=1,
    )
    test_db.add(q1)
    test_db.commit()
    ans1 = Answer(session_id=sess.id, question_id=q1.id, user_id=test_user.id, answer_text="Ans 1")
    test_db.add(ans1)
    test_db.commit()
    eval1 = AnswerEvaluation(answer_id=ans1.id, question_id=q1.id, overall_score=80.0, feedback="Good")
    test_db.add(eval1)
    test_db.commit()

    # Question 2: Generated but NOT answered / NOT evaluated
    q2 = InterviewQuestion(
        session_id=sess.id,
        question_text="Q2 text",
        question_type="mixed",
        difficulty="medium",
        skill="FastAPI",
        bloom_level="remember",
        bloom_level_number=1,
        question_number=2,
    )
    test_db.add(q2)
    test_db.commit()

    # Calculate comparison
    comparisons = get_skill_comparison(test_db, sess)
    assert len(comparisons) == 1
    comp = comparisons[0]
    # Current score must be 80.0, NOT (80 + 0) / 2 = 40.0!
    assert comp["current_score"] == 80.0
    assert comp["previous_score"] == 45.0
    assert comp["change"] == 35.0
    assert comp["status"] == "improved"


def test_user_with_four_eligible_weak_skills_receives_all_four(test_db, test_user):
    """
    Test that a candidate with FOUR qualifying weak skills (>= 2 assessments each and avg < 65)
    receives all 4 skills in:
    - get_weak_skill_profiles["weak_skills"]
    - get_user_performance["weak_areas"]
    - GET /api/users/weak-skills
    - GET /api/users/performance
    No arbitrary limits or truncations apply.
    """
    evals = [
        # Skill 1: Java (avg 42.5 -> weak)
        {"skill": "Java", "overall_score": 40.0},
        {"skill": "Java", "overall_score": 45.0},
        # Skill 2: Python (avg 45.0 -> weak)
        {"skill": "Python", "overall_score": 42.0},
        {"skill": "Python", "overall_score": 48.0},
        # Skill 3: SQL (avg 55.0 -> needs_practice)
        {"skill": "SQL", "overall_score": 52.0},
        {"skill": "SQL", "overall_score": 58.0},
        # Skill 4: Docker (avg 60.0 -> needs_practice)
        {"skill": "Docker", "overall_score": 58.0},
        {"skill": "Docker", "overall_score": 62.0},
        # Skill 5: Strong skill (avg 90.0 -> strong, NOT weak)
        {"skill": "Kubernetes", "overall_score": 88.0},
        {"skill": "Kubernetes", "overall_score": 92.0},
    ]
    _create_completed_session_with_evals(test_db, test_user.id, evals)

    # 1. Service direct call
    profiles = get_weak_skill_profiles(test_db, test_user.id)
    weak_skills = profiles["weak_skills"]
    assert len(weak_skills) == 4
    weak_names = [w["skill"] for w in weak_skills]
    assert set(weak_names) == {"Java", "Python", "SQL", "Docker"}
    # Verify sorted weakest first
    scores = [w["average_score"] for w in weak_skills]
    assert scores == sorted(scores)

    # 2. Performance unification direct call
    perf = get_user_performance(test_db, test_user.id)
    assert len(perf["weak_areas"]) == 4
    assert set(perf["weak_areas"]) == {"Java", "Python", "SQL", "Docker"}
    assert perf["weak_areas"] == weak_names

    # 3. HTTP API integration via TestClient
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    token = create_access_token(user_id=test_user.id)
    headers = {"Authorization": f"Bearer {token}"}

    res_weak = client.get("/api/users/weak-skills", headers=headers)
    assert res_weak.status_code == 200
    data_weak = res_weak.json()
    assert len(data_weak["weak_skills"]) == 4
    assert [w["skill"] for w in data_weak["weak_skills"]] == weak_names

    res_perf = client.get("/api/users/performance", headers=headers)
    assert res_perf.status_code == 200
    data_perf = res_perf.json()
    assert len(data_perf["weak_areas"]) == 4
    assert data_perf["weak_areas"] == weak_names

    app.dependency_overrides.clear()


def test_user_with_one_eligible_weak_skill_receives_one(test_db, test_user):
    """
    Test that a candidate with exactly ONE qualifying weak skill receives only that one,
    while skills with insufficient assessments (count=1) are protected from being classified as weak.
    """
    evals = [
        # Skill 1: Java (2 evals, avg 45.0 -> weak)
        {"skill": "Java", "overall_score": 40.0},
        {"skill": "Java", "overall_score": 50.0},
        # Skills with only 1 eval: protected under MIN_ASSESSMENTS_FOR_WEAK
        {"skill": "C", "overall_score": 0.0},
        {"skill": "PostgreSQL", "overall_score": 0.0},
        {"skill": "React", "overall_score": 15.0},
        # Skill with strong score
        {"skill": "Go", "overall_score": 90.0},
        {"skill": "Go", "overall_score": 95.0},
    ]
    _create_completed_session_with_evals(test_db, test_user.id, evals)

    profiles = get_weak_skill_profiles(test_db, test_user.id)
    weak_skills = profiles["weak_skills"]
    assert len(weak_skills) == 1
    assert weak_skills[0]["skill"] == "Java"
    assert weak_skills[0]["classification"] == "weak"

    perf = get_user_performance(test_db, test_user.id)
    assert len(perf["weak_areas"]) == 1
    assert perf["weak_areas"] == ["Java"]


def test_user_with_no_eligible_weak_skills_receives_empty(test_db, test_user):
    """
    Test that a candidate with no qualifying weak skills receives an empty list.
    """
    evals = [
        {"skill": "Python", "overall_score": 85.0},
        {"skill": "Python", "overall_score": 90.0},
        {"skill": "Docker", "overall_score": 75.0},
        {"skill": "Docker", "overall_score": 80.0},
    ]
    _create_completed_session_with_evals(test_db, test_user.id, evals)

    profiles = get_weak_skill_profiles(test_db, test_user.id)
    assert profiles["weak_skills"] == []

    perf = get_user_performance(test_db, test_user.id)
    assert perf["weak_areas"] == []


def test_analytics_and_weak_skills_endpoints_unified_source_of_truth(test_db, test_user):
    """
    Verify architectural contract:
    Analytics dashboard and Weak Areas modal must always return the exact same weak skills list.
    """
    evals = [
        {"skill": "Java", "overall_score": 30.0},
        {"skill": "Java", "overall_score": 35.0},
        {"skill": "C", "overall_score": 10.0},  # 1 eval -> insufficient data
        {"skill": "Python", "overall_score": 55.0},
        {"skill": "Python", "overall_score": 60.0},  # 2 evals, avg 57.5 -> needs_practice
    ]
    _create_completed_session_with_evals(test_db, test_user.id, evals)

    profiles = get_weak_skill_profiles(test_db, test_user.id)
    perf = get_user_performance(test_db, test_user.id)

    expected_weak = [w["skill"] for w in profiles["weak_skills"]]
    assert expected_weak == ["Java", "Python"]
    assert perf["weak_areas"] == expected_weak
    assert "C" not in perf["weak_areas"]


def test_skill_name_casing_normalization(test_db, test_user):
    """
    Skills with equivalent normalized names (e.g. 'python', 'Python', 'PYTHON')
    are aggregated together rather than counted as separate skills.
    """
    evals = [
        {"skill": "Python", "overall_score": 40.0},
        {"skill": "python", "overall_score": 44.0},
        {"skill": "PYTHON", "overall_score": 42.0},
    ]
    _create_completed_session_with_evals(test_db, test_user.id, evals)

    profiles = get_weak_skill_profiles(test_db, test_user.id)
    assert len(profiles["weak_skills"]) == 1
    assert profiles["weak_skills"][0]["skill"] == "Python"
    assert profiles["weak_skills"][0]["assessment_count"] == 3
    assert profiles["weak_skills"][0]["average_score"] == 42.0




