from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.attempt import AttemptResponse, AttemptSubmit
from app.crud.attempt import create_attempt as create_attempt_record, get_attempts as get_attempt_records
from app.services.submit_service import submit_solution

router = APIRouter()

@router.get("/attempts", response_model=list[AttemptResponse])
def get_attempts(
    db: Session = Depends(get_db),
    user_id: int | None = None,
    problem_id: int | None = None
):
    return get_attempt_records(db, user_id, problem_id)

# TODO - user_id shouldn't come from Front end, should come from auth token. For now, we will pass it as a query param for testing.
@router.post("/attempt/submit", response_model=AttemptResponse)
def submit_attempt(attempt: AttemptSubmit, user_id: int, db: Session = Depends(get_db)):
    evaluation = submit_solution(attempt, db)
    return create_attempt_record(attempt, evaluation, user_id, db)
