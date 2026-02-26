# DB Table Models

from uuid import uuid4
from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


def generate_submission_id() -> str:
    return f"submission_{uuid4().hex[:12]}"


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(String(64), primary_key=True, index=True, default=generate_submission_id)
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False)
    problem_id = Column(String(64), ForeignKey("problems.id"), nullable=False)
    code_submitted = Column(Text, nullable=False) # Code submitted by the user for this submission
    language = Column(String(20), nullable=False, index=True)
    result = Column(String(20), nullable=False)  # e.g., "pass", "fail"
    created_at = Column(DateTime, default=datetime.utcnow)
    error = Column(Text, nullable=True)

    user = relationship("User", back_populates="submissions")
    problem = relationship("Problem", back_populates="submissions")
