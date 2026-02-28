from uuid import uuid4
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


def generate_user_id() -> str:
    return f"user_{uuid4().hex[:12]}"


class User(Base):
    __tablename__ = "users"
    
    id = Column(String(64), primary_key=True, index=True, default=generate_user_id)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at= Column(DateTime, default=datetime.utcnow)

    submissions = relationship("Submission", back_populates="user")
    user_problems = relationship("UserProblem", back_populates="user", cascade="all, delete-orphan")
    interview_sessions = relationship("InterviewSession", back_populates="user", cascade="all, delete-orphan")
    interview_messages = relationship("InterviewMessage", back_populates="user")
