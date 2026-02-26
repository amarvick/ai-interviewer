from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base


def generate_user_problem_id() -> str:
    return f"user_problem_{uuid4().hex[:12]}"


class UserProblem(Base):
    __tablename__ = "user_problems"
    __table_args__ = (
        UniqueConstraint("user_id", "problem_id", name="uq_user_problem"),
    )

    id = Column(String(64), primary_key=True, index=True, default=generate_user_problem_id)
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    problem_id = Column(String(64), ForeignKey("problems.id"), nullable=False, index=True)

    is_passed = Column(Boolean, nullable=False, default=False)
    first_passed_at = Column(DateTime, nullable=True)
    last_submission_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_submission_id = Column(String(64), ForeignKey("submissions.id"), nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="user_problems")
    problem = relationship("Problem", back_populates="user_problems")
    last_submission = relationship("Submission", foreign_keys=[last_submission_id])
