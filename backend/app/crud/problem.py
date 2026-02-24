from sqlalchemy.orm import Session
from app.db.models.problem import Problem
from app.db.models.problem_list import ProblemList
from app.db.models.problem_list_problem import ProblemListProblem

# For problem page
def get_problem_by_id(db, problem_id: str):
    return db.query(Problem).filter(Problem.id == problem_id).first()

# For home page
def get_problem_lists(db: Session):
    return db.query(ProblemList).all()

# For problem list page
def get_problem_list_name_by_id(db: Session, problem_list_id: str):
    problem_list = db.query(ProblemList).filter(ProblemList.id == problem_list_id).first()
    return problem_list.name if problem_list else None

def get_problems_from_problem_list(db: Session, problem_list_id: str):
    return (
        db.query(Problem)
        .join(ProblemListProblem, ProblemListProblem.problem_id == Problem.id)
        .filter(ProblemListProblem.problem_list_id == problem_list_id)
        .all()
    )
