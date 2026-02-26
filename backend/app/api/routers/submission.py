from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.submission import SubmissionResponse, SubmissionSubmit
from app.core.constants import Language
from app.crud.submission import create_submission as create_submission_record, get_submissions as get_submission_records
from app.services.submit_service import submit_solution
from app.core.auth import get_current_user
from app.db.models.user import User

router = APIRouter()

@router.get("/submissions", response_model=list[SubmissionResponse])
def get_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    problem_id: str | None = None,
    language: Language | None = None,
):
    return get_submission_records(
        db=db,
        user_id=current_user.id,
        problem_id=problem_id,
        language=language,
    )

@router.post("/submission/submit", response_model=SubmissionResponse)
def submit_submission(submission: SubmissionSubmit, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    evaluation = submit_solution(submission, db)
    print("Evaluation result:", evaluation)
    return create_submission_record(submission, evaluation, current_user.id, db)
