from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.db.database import Base


def generate_interview_session_id() -> str:
    return f"interview_session_{uuid4().hex[:12]}"


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(
        String(64),
        primary_key=True,
        index=True,
        default=generate_interview_session_id,
    )
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    problem_id = Column(String(64), ForeignKey("problems.id"), nullable=False, index=True)

    stage = Column(String(40), nullable=False, default="INTRO")
    status = Column(String(20), nullable=False, default="ACTIVE")
    final_score = Column(Float, nullable=True)

    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="interview_sessions")
    problem = relationship("Problem", back_populates="interview_sessions")
    messages = relationship(
        "InterviewMessage",
        back_populates="session",
        cascade="all, delete-orphan",
    )
    evaluations = relationship(
        "InterviewEvaluation",
        back_populates="session",
        cascade="all, delete-orphan",
    )
