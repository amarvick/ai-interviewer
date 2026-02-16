from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.attempt import AttemptCreate, AttemptResponse
from app.db.models.attempt import Attempt

router = APIRouter()

@router.post("/attempt", response_model=AttemptCreate)
def create_attempt(attempt: AttemptCreate, db: Session = Depends(get_db)):
    db_attempt = Attempt(
        title=attempt.code_submitted,
    )
    db.add(db_attempt)
    db.commit()
    db.refresh(db_attempt)
    return db_attempt

# TODO - should get attempts by user_id AND problem_id
@router.get("/attempts", response_model=list[AttemptResponse])
def get_attempts(db: Session = Depends(get_db)):
    attempts = db.query(Attempt).all()
    return attempts
