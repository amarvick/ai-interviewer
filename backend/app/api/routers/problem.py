from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.problem import ProblemCreate, ProblemResponse
from app.crud.problem import create_problem, get_problems

router = APIRouter()

@router.post("/problems", response_model=ProblemCreate)
def create_problem(problem: ProblemCreate, db: Session = Depends(get_db)):
    return create_problem(problem, db)

@router.get("/problems", response_model=list[ProblemResponse])
def get_problems(db: Session = Depends(get_db)):
    return get_problems(db)
