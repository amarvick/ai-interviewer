from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.problem import (
    ProblemCreate,
    ProblemListProblemsResponse,
    ProblemListResponse,
    ProblemResponse,
)
from app.crud.problem import (
    create_problem as create_problem_record,
    get_problem_lists as get_problem_list_records,
    get_problems_from_problem_list as get_problems_from_problem_list_record,
    get_problem_list_name_by_id,
    get_problem_by_id as get_problem_by_id_record,
)
from app.crud.testcase import get_public_testcases_by_problem_id

router = APIRouter()

@router.post("/problem", response_model=ProblemResponse)
def create_problem(problem: ProblemCreate, db: Session = Depends(get_db)):
    return create_problem_record(problem, db)

@router.get("/problem-lists", response_model=list[ProblemListResponse])
def get_problem_lists(db: Session = Depends(get_db)):
    return get_problem_list_records(db)

@router.get("/problems/{problem_list_id}", response_model=ProblemListProblemsResponse)
def get_problems_from_problem_list(problem_list_id: str, db: Session = Depends(get_db)):
    list_name = get_problem_list_name_by_id(db, problem_list_id)
    if list_name is None:
        raise HTTPException(status_code=404, detail="Problem list not found")

    problems = get_problems_from_problem_list_record(db, problem_list_id)
    return {"name": list_name, "problems": problems}

@router.get("/problem/{problem_id}", response_model=ProblemResponse)
def get_problem_by_id(problem_id: str, db: Session = Depends(get_db)):
    problem = get_problem_by_id_record(db, problem_id)
    if problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    test_cases = get_public_testcases_by_problem_id(db, problem_id)
    problem.test_cases = test_cases
    return problem
