from uuid import uuid4
from sqlalchemy import Column, JSON, Boolean, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


def generate_testcase_id() -> str:
    return f"testcase_{uuid4().hex[:12]}"


class TestCase(Base):
    __tablename__ = "testcases"

    id = Column(String(64), primary_key=True, index=True, default=generate_testcase_id)
    problem_id = Column(String(64), ForeignKey("problems.id"), nullable=False)

    params = Column(JSON, nullable=False)
    expected_output = Column(JSON, nullable=False)

    is_hidden = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    problem = relationship("Problem", back_populates="testcases")
