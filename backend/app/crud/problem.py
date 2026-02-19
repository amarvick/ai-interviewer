from sqlalchemy.orm import Session
from app.db.models.problem import Problem
from app.db.models.problem_list import ProblemList
from app.db.models.problem_list_problem import ProblemListProblem
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


def get_problem_lists(db: Session):
    return db.query(ProblemList).all()

def get_problems_from_problem_list(db: Session, problem_list_id: str):
    print("Getting problems for problem list ID:", problem_list_id)
    return (
        db.query(Problem)
        .join(ProblemListProblem, ProblemListProblem.problem_id == Problem.id)
        .filter(ProblemListProblem.problem_list_id == problem_list_id)
        .all()
    )
