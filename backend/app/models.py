# DB Table Models

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at= Column(DateTime, default=datetime.utcnow)

    attempts = relationship("Attempt", back_populates="user")

class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), index=True, nullable=False)
    difficulty = Column(String(20), index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # _links is meant to point to the middleman between two tables with many to many relationships, with back_populates being that other object
    # If a link is deleted, cascade="all, delete-orphan" deletes the link row (ProblemListProblem) but NOT the individual objects (ProblemList or Problem).
    problem_list_links = relationship("ProblemListProblem", back_populates="problem", cascade="all, delete-orphan")
    # This is the relationship to the other object, where secondary has to be the name of middleman table.
    problem_lists = relationship("ProblemList", secondary="problem_list_problems", back_populates="problems")
    attempts = relationship("Attempt", back_populates="problem")

class ProblemList(Base):
    __tablename__ = "problem_lists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    icon_url = Column(String, index=True, nullable=False)
    created_at= Column(DateTime, default=datetime.utcnow)
    
    problem_links = relationship("ProblemListProblem", back_populates="problem_list", cascade="all, delete-orphan")
    problems = relationship("Problem", secondary="problem_list_problems", back_populates="problem_lists")

# Association table for many-to-many relationship between ProblemList and Problem
class ProblemListProblem(Base):
    __tablename__ = "problem_list_problems"
    __table_args__ = (
        UniqueConstraint("problem_list_id", "problem_id", name="uq_problem_list_problem"),
    )

    id = Column(Integer, primary_key=True, index=True)
    problem_list_id = Column(Integer, ForeignKey("problem_lists.id"), nullable=False)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)

    problem_list = relationship("ProblemList", back_populates="problem_links")
    problem = relationship("Problem", back_populates="problem_list_links")   

class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    code_submitted = Column(Text, nullable=False) # Code submitted by the user for this attempt
    result = Column(String(20), nullable=False)  # e.g., "passed", "failed"
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="attempts")
    problem = relationship("Problem", back_populates="attempts")
