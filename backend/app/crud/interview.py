from sqlalchemy.orm import Session, joinedload
from app.db.models.interview_session import InterviewSession
from app.db.models.interview_message import InterviewMessage
from app.db.models.interview_evaluation import InterviewEvaluation


def create_interview_session(db: Session, user_id: str, problem_id: str) -> InterviewSession:
    session = InterviewSession(
        user_id=user_id,
        problem_id=problem_id,
        stage="INTRO",
        status="ACTIVE",
    )
    db.add(session)
    db.flush()
    return session


def get_interview_session_by_id(db: Session, session_id: str) -> InterviewSession | None:
    return (
        db.query(InterviewSession)
        .options(
            joinedload(InterviewSession.messages),
            joinedload(InterviewSession.evaluations),
        )
        .filter(InterviewSession.id == session_id)
        .first()
    )


def create_interview_message(
    db: Session,
    session_id: str,
    role: str,
    content: str,
    stage_at_message: str,
    user_id: str | None = None,
) -> InterviewMessage:
    message = InterviewMessage(
        session_id=session_id,
        user_id=user_id,
        role=role,
        content=content,
        stage_at_message=stage_at_message,
    )
    db.add(message)
    db.flush()
    return message


def create_interview_evaluation(
    db: Session,
    session_id: str,
    stage: str,
    summary: str,
    problem_understanding_score: int = 0,
    approach_quality_score: int = 0,
    code_correctness_reasoning_score: int = 0,
    complexity_analysis_score: int = 0,
    communication_clarity_score: int = 0,
    total_score: float = 0,
    passed: bool = False,
    rubric_json: dict | None = None,
) -> InterviewEvaluation:
    evaluation = InterviewEvaluation(
        session_id=session_id,
        stage=stage,
        problem_understanding_score=problem_understanding_score,
        approach_quality_score=approach_quality_score,
        code_correctness_reasoning_score=code_correctness_reasoning_score,
        complexity_analysis_score=complexity_analysis_score,
        communication_clarity_score=communication_clarity_score,
        total_score=total_score,
        passed=passed,
        summary=summary,
        rubric_json=rubric_json or {},
    )
    db.add(evaluation)
    db.flush()
    return evaluation


def get_recent_messages_by_session_id(
    db: Session,
    session_id: str,
    limit: int = 8,
) -> list[InterviewMessage]:
    return (
        db.query(InterviewMessage)
        .filter(InterviewMessage.session_id == session_id)
        .order_by(InterviewMessage.created_at.desc())
        .limit(limit)
        .all()
    )


def get_recent_evaluations_by_session_id(
    db: Session,
    session_id: str,
    limit: int = 3,
) -> list[InterviewEvaluation]:
    return (
        db.query(InterviewEvaluation)
        .filter(InterviewEvaluation.session_id == session_id)
        .order_by(InterviewEvaluation.created_at.desc())
        .limit(limit)
        .all()
    )
