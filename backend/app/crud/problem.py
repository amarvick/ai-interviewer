from sqlalchemy.orm import Session
from app.db.models.problem import Problem
from app.schemas.problem import ProblemCreate

def create_problem(problem: ProblemCreate, db: Session):
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

def get_problems(db: Session):
    problems = db.query(Problem).all()
    return problems

def get_problem_by_id(db, problem_id: int):
    return db.query(Problem).filter(Problem.id == problem_id).first()