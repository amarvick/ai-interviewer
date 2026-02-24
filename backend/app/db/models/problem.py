from sqlalchemy import Column, Integer, Text, String, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), index=True, nullable=False)
    difficulty = Column(String(20), index=True, nullable=False)
    starter_code = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    # _links is meant to point to the middleman between two tables with many to many relationships, with back_populates being that other object
    # If a link is deleted, cascade="all, delete-orphan" deletes the link row (ProblemListProblem) but NOT the individual objects (ProblemList or Problem).
    problem_list_links = relationship("ProblemListProblem", back_populates="problem", cascade="all, delete-orphan")
    # This is the relationship to the other object, where secondary has to be the name of middleman table.
    problem_lists = relationship("ProblemList", secondary="problem_list_problems", back_populates="problems")
    submissions = relationship("Submission", back_populates="problem")
    testcases = relationship("TestCase", back_populates="problem", cascade="all, delete-orphan")
