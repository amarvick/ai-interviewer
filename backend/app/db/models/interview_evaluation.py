from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, Boolean, JSON, CheckConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base


def generate_interview_evaluation_id() -> str:
    return f"interview_eval_{uuid4().hex[:12]}"


class InterviewEvaluation(Base):
    __tablename__ = "interview_evaluations"
    __table_args__ = (
        CheckConstraint("problem_understanding_score BETWEEN 0 AND 2", name="ck_eval_problem_understanding"),
        CheckConstraint("approach_quality_score BETWEEN 0 AND 2", name="ck_eval_approach_quality"),
        CheckConstraint("code_correctness_reasoning_score BETWEEN 0 AND 2", name="ck_eval_code_reasoning"),
        CheckConstraint("complexity_analysis_score BETWEEN 0 AND 2", name="ck_eval_complexity"),
        CheckConstraint("communication_clarity_score BETWEEN 0 AND 2", name="ck_eval_communication"),
    )

    id = Column(
        String(64),
        primary_key=True,
        index=True,
        default=generate_interview_evaluation_id,
    )
    session_id = Column(
        String(64),
        ForeignKey("interview_sessions.id"),
        nullable=False,
        index=True,
    )

    stage = Column(String(40), nullable=False)

    problem_understanding_score = Column(Integer, nullable=False, default=0)
    approach_quality_score = Column(Integer, nullable=False, default=0)
    code_correctness_reasoning_score = Column(Integer, nullable=False, default=0)
    complexity_analysis_score = Column(Integer, nullable=False, default=0)
    communication_clarity_score = Column(Integer, nullable=False, default=0)

    total_score = Column(Float, nullable=False, default=0)
    passed = Column(Boolean, nullable=False, default=False)

    summary = Column(String(500), nullable=True)
    rubric_json = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    session = relationship("InterviewSession", back_populates="evaluations")
