from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class ProblemList(Base):
    __tablename__ = "problem_lists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    icon_url = Column(String, index=True, nullable=False)
    created_at= Column(DateTime, default=datetime.utcnow)
    
    problem_links = relationship("ProblemListProblem", back_populates="problem_list", cascade="all, delete-orphan")
    problems = relationship("Problem", secondary="problem_list_problems", back_populates="problem_lists")
