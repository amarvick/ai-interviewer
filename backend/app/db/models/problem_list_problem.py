from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base

# Association table for many-to-many relationship between ProblemList and Problem
class ProblemListProblem(Base):
    __tablename__ = "problem_list_problems"
    __table_args__ = (
        UniqueConstraint("problem_list_id", "problem_id", name="uq_problem_list_problem"),
    )

    id = Column(Integer, primary_key=True, index=True)
    problem_list_id = Column(String, ForeignKey("problem_lists.id"), nullable=False)
    problem_id = Column(String(64), ForeignKey("problems.id"), nullable=False)

    problem_list = relationship("ProblemList", back_populates="problem_links")
    problem = relationship("Problem", back_populates="problem_list_links")   
