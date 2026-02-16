from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.attempt import Attempt
from app.schemas.attempt import AttemptCreate

def create_attempt(attempt: AttemptCreate, db: Session = Depends(get_db), user_id: int = 1, problem_id: int = 1):
    db_attempt = Attempt(
        code_submitted=attempt.code_submitted,
        result=attempt.result,
        user_id=user_id,
        problem_id=problem_id
    )
    db.add(db_attempt)
    db.commit()
    db.refresh(db_attempt)
    return db_attempt 

def get_attempts(db: Session = Depends(get_db), user_id: int = 1, problem_id: int = 1):
    attempts = db.query(Attempt).filter(
        Attempt.user_id == user_id,
        Attempt.problem_id == problem_id
    ).all()
    return attempts