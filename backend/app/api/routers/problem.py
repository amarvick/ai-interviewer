from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.problem import ProblemCreate, ProblemResponse
from app.crud.problem import create_problem as create_problem_record, get_problems as get_problem_records

router = APIRouter()

@router.post("/problem", response_model=ProblemResponse)
def create_problem(problem: ProblemCreate, db: Session = Depends(get_db)):
    return create_problem_record(problem, db)

@router.get("/problem", response_model=list[ProblemResponse])
def get_problems(db: Session = Depends(get_db)):
    return get_problem_records(db)
