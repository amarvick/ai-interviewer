from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.problem import (
    ProblemListProblemsResponse,
    ProblemListResponse,
    ProblemResponse,
)
from app.crud.problem import (
    get_problem_lists as get_problem_list_records,
    get_problems_from_problem_list as get_problems_from_problem_list_record,
    get_passed_problem_ids_for_user,
    get_problem_list_name_by_id,
    get_problem_by_id as get_problem_by_id_record,
)
from app.crud.testcase import get_public_testcases_by_problem_id
from app.core.auth import get_current_user_optional
from app.db.models.user import User

router = APIRouter()

@router.get("/problem-lists", response_model=list[ProblemListResponse])
def get_problem_lists(db: Session = Depends(get_db)):
    return get_problem_list_records(db)

@router.get("/problems/{problem_list_id}", response_model=ProblemListProblemsResponse)
def get_problems_from_problem_list(
    problem_list_id: str,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    list_name = get_problem_list_name_by_id(db, problem_list_id)
    if list_name is None:
        raise HTTPException(status_code=404, detail="Problem list not found")

    problems = get_problems_from_problem_list_record(db, problem_list_id)
    passed_problem_ids: set[str] = set()
    if current_user is not None:
        passed_problem_ids = get_passed_problem_ids_for_user(
            db=db,
            user_id=current_user.id,
            problem_ids=[problem.id for problem in problems],
        )
    for problem in problems:
        problem.is_passed = problem.id in passed_problem_ids
    return {"name": list_name, "problems": problems}

@router.get("/problem/{problem_id}", response_model=ProblemResponse)
def get_problem_by_id(problem_id: str, db: Session = Depends(get_db)):
    problem = get_problem_by_id_record(db, problem_id)
    if problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    test_cases = get_public_testcases_by_problem_id(db, problem_id)
    problem.test_cases = test_cases
    return problem
