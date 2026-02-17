from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import cast
from app.db.database import get_db
from app.schemas.attempt import AttemptResponse, AttemptSubmit
from app.crud.attempt import create_attempt as create_attempt_record, get_attempts as get_attempt_records
from app.services.submit_service import submit_solution
from app.core.auth import get_current_user
from app.db.models.user import User

router = APIRouter()

@router.get("/attempts", response_model=list[AttemptResponse])
def get_attempts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    problem_id: int | None = None
):
    return get_attempt_records(db, cast(int, current_user.id), problem_id)

@router.post("/attempt/submit", response_model=AttemptResponse)
def submit_attempt(attempt: AttemptSubmit, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    evaluation = submit_solution(attempt, db)
    return create_attempt_record(attempt, evaluation, cast(int, current_user.id), db)
