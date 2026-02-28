from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.database import Base


def generate_interview_message_id() -> str:
    return f"interview_message_{uuid4().hex[:12]}"


class InterviewMessage(Base):
    __tablename__ = "interview_messages"

    id = Column(
        String(64),
        primary_key=True,
        index=True,
        default=generate_interview_message_id,
    )
    session_id = Column(
        String(64),
        ForeignKey("interview_sessions.id"),
        nullable=False,
        index=True,
    )
    # Present for user-authored messages; null for system/assistant messages.
    user_id = Column(String(64), ForeignKey("users.id"), nullable=True, index=True)

    role = Column(String(20), nullable=False)  # system | assistant | user
    content = Column(Text, nullable=False)
    stage_at_message = Column(String(40), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    session = relationship("InterviewSession", back_populates="messages")
    user = relationship("User", back_populates="interview_messages")
