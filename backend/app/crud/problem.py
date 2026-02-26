from sqlalchemy.orm import Session
from app.db.models.problem import Problem
from app.db.models.problem_list import ProblemList
from app.db.models.problem_list_problem import ProblemListProblem
from app.db.models.user_problem import UserProblem

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


def get_passed_problem_ids_for_user(
    db: Session,
    user_id: str,
    problem_ids: list[str],
) -> set[str]:
    if not problem_ids:
        return set()
    rows = (
        db.query(UserProblem.problem_id)
        .filter(
            UserProblem.user_id == user_id,
            UserProblem.problem_id.in_(problem_ids),
            UserProblem.is_passed.is_(True),
        )
        .all()
    )
    return {row[0] for row in rows}
