from sqlalchemy.orm import Session
from app.db.models.submission import Submission
from app.schemas.submission import SubmissionSubmit

def create_submission(submission: SubmissionSubmit, evaluation: dict, user_id: int, db: Session):
    result = str(evaluation.get("result"))

    db_submission = Submission(
        code_submitted=submission.code_submitted,
        result=result,
        user_id=user_id,
        problem_id=submission.problem_id,
        error=evaluation.get("error_message")
    )
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission

def get_submissions(db: Session, user_id: int | None = None, problem_id: int | None = None):
    query = db.query(Submission)
    if user_id is not None:
        query = query.filter(Submission.user_id == user_id)
    if problem_id is not None:
        query = query.filter(Submission.problem_id == problem_id)
    return query.all()
