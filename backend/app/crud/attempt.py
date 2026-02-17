from sqlalchemy.orm import Session
from app.db.models.attempt import Attempt
from app.schemas.attempt import AttemptSubmit

def create_attempt(attempt: AttemptSubmit, evaluation: dict, user_id: int, db: Session):
    result = str(evaluation.get("result"))

    db_attempt = Attempt(
        code_submitted=attempt.code_submitted,
        result=result,
        user_id=user_id,
        problem_id=attempt.problem_id,
        error=evaluation.get("error_message")
    )
    db.add(db_attempt)
    db.commit()
    db.refresh(db_attempt)
    return db_attempt 

def get_attempts(db: Session, user_id: int | None = None, problem_id: int | None = None):
    query = db.query(Attempt)
    if user_id is not None:
        query = query.filter(Attempt.user_id == user_id)
    if problem_id is not None:
        query = query.filter(Attempt.problem_id == problem_id)
    return query.all()
