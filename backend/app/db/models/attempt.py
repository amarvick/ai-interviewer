# DB Table Models

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    code_submitted = Column(Text, nullable=False) # Code submitted by the user for this attempt
    result = Column(String(20), nullable=False)  # e.g., "pass", "fail"
    created_at = Column(DateTime, default=datetime.utcnow)
    error = Column(Text, nullable=True)

    user = relationship("User", back_populates="attempts")
    problem = relationship("Problem", back_populates="attempts")
