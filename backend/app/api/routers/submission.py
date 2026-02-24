from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import cast
from app.db.database import get_db
from app.schemas.submission import SubmissionResponse, SubmissionSubmit
from app.crud.submission import create_submission as create_submission_record, get_submissions as get_submission_records
from app.services.submit_service import submit_solution
from app.core.auth import get_current_user
from app.db.models.user import User

router = APIRouter()

@router.get("/submissions", response_model=list[SubmissionResponse])
def get_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    problem_id: int | None = None
):
    return get_submission_records(db, cast(int, current_user.id), problem_id)

@router.post("/submission/submit", response_model=SubmissionResponse)
def submit_submission(submission: SubmissionSubmit, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    evaluation = submit_solution(submission, db)
    return create_submission_record(submission, evaluation, cast(int, current_user.id), db)
