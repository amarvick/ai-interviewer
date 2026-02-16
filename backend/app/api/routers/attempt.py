from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.attempt import AttemptCreate, AttemptResponse
from app.crud.attempt import create_attempt as create_attempt_record, get_attempts as get_attempt_records

router = APIRouter()

@router.post("/attempt", response_model=AttemptResponse)
def create_attempt(attempt: AttemptCreate, db: Session = Depends(get_db)):
    return create_attempt_record(attempt, db)

@router.get("/attempts", response_model=list[AttemptResponse])
def get_attempts(
    db: Session = Depends(get_db),
    user_id: int | None = None,
    problem_id: int | None = None
):
    return get_attempt_records(db, user_id, problem_id)
