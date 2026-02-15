# DB Table Models

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
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

class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    code_submitted = Column(Text, nullable=False)
    result = Column(String(20), nullable=False)  # e.g., "passed", "failed"
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="attempts")
    problem = relationship("Problem", back_populates="attempts")