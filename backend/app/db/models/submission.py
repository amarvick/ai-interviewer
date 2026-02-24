# DB Table Models

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    code_submitted = Column(Text, nullable=False) # Code submitted by the user for this submission
    result = Column(String(20), nullable=False)  # e.g., "pass", "fail"
    created_at = Column(DateTime, default=datetime.utcnow)
    error = Column(Text, nullable=True)

    user = relationship("User", back_populates="submissions")
    problem = relationship("Problem", back_populates="submissions")
