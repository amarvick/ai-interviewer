from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base

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
