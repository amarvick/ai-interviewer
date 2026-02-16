from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.problem import Problem
from app.schemas.problem import ProblemCreate

def create_problem(problem: ProblemCreate, db: Session = Depends(get_db)):
    db_problem = Problem(
        title=problem.title,
        description=problem.description,
        difficulty=problem.difficulty,
        category=problem.category
    )
    db.add(db_problem)
    db.commit()
    db.refresh(db_problem)
    return db_problem 

def get_problems(db: Session = Depends(get_db)):
    problems = db.query(Problem).all()
    return problems