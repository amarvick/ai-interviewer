from uuid import uuid4
from sqlalchemy import Column, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base


def generate_problem_list_problem_id() -> str:
    return f"plp_{uuid4().hex[:12]}"


class ProblemListProblem(Base):
    __tablename__ = "problem_list_problems"
    __table_args__ = (
        UniqueConstraint("problem_list_id", "problem_id", name="uq_problem_list_problem"),
    )

    id = Column(String(64), primary_key=True, index=True, default=generate_problem_list_problem_id)
    problem_list_id = Column(String(64), ForeignKey("problem_lists.id"), nullable=False)
    problem_id = Column(String(64), ForeignKey("problems.id"), nullable=False)

    problem_list = relationship("ProblemList", back_populates="problem_links")
    problem = relationship("Problem", back_populates="problem_list_links")   
