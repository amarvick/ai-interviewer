from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.testcase import TestCaseCreate, TestCaseResponse
from app.crud.testcase import create_testcase, get_testcases_by_problem_id

router = APIRouter()


@router.post("/testcases", response_model=TestCaseResponse)
def create_testcase_route(testcase: TestCaseCreate, db: Session = Depends(get_db)):
    return create_testcase(testcase, db)


@router.get("/problems/{problem_id}/testcases", response_model=list[TestCaseResponse])
def get_testcases_by_problem(problem_id: str, db: Session = Depends(get_db)):
    return get_testcases_by_problem_id(db, problem_id)
