from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base


class UserProblem(Base):
    __tablename__ = "user_problems"
    __table_args__ = (
        UniqueConstraint("user_id", "problem_id", name="uq_user_problem"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    problem_id = Column(String(64), ForeignKey("problems.id"), nullable=False, index=True)

    is_passed = Column(Boolean, nullable=False, default=False)
    first_passed_at = Column(DateTime, nullable=True)
    last_submission_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="user_problems")
    problem = relationship("Problem", back_populates="user_problems")
    last_submission = relationship("Submission", foreign_keys=[last_submission_id])

