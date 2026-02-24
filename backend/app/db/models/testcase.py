from sqlalchemy import Column, Integer, JSON, Boolean, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class TestCase(Base):
    __tablename__ = "testcases"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(String(64), ForeignKey("problems.id"), nullable=False)

    params = Column(JSON, nullable=False)
    expected_output = Column(JSON, nullable=False)

    is_hidden = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    problem = relationship("Problem", back_populates="testcases")
