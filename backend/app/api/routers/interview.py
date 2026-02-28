from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.database import get_db
from app.db.models.user import User
from app.schemas.interview import (
    InterviewMessageCreate,
    InterviewSessionComplete,
    InterviewSessionCreate,
    InterviewSessionDetailResponse,
    InterviewSessionResponse,
)
from app.services.interview_service import (
    complete_interview_session,
    process_interview_message,
    start_interview_session,
)
from app.crud.interview import get_interview_session_by_id

router = APIRouter(prefix="/interview", tags=["interview"])


@router.post("/session/start", response_model=InterviewSessionResponse)
def create_interview_session(
    payload: InterviewSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = start_interview_session(
        db=db,
        user_id=current_user.id,
        problem_id=payload.problem_id,
    )
    if session is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    return session


@router.get("/session/{session_id}", response_model=InterviewSessionDetailResponse)
def get_interview_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = get_interview_session_by_id(db, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Interview session not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return session


@router.post("/session/{session_id}/message", response_model=InterviewSessionDetailResponse)
def post_interview_message(
    session_id: str,
    payload: InterviewMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing_session = get_interview_session_by_id(db, session_id)
    if existing_session is None:
        raise HTTPException(status_code=404, detail="Interview session not found")
    if existing_session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    session = process_interview_message(
        db=db,
        session_id=session_id,
        user_id=current_user.id,
        content=payload.content,
        has_submission=payload.has_submission,
    )
    if session is None:
        raise HTTPException(status_code=404, detail="Interview session not found")
    return session


@router.post("/session/{session_id}/complete", response_model=InterviewSessionResponse)
def complete_session(
    session_id: str,
    payload: InterviewSessionComplete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing_session = get_interview_session_by_id(db, session_id)
    if existing_session is None:
        raise HTTPException(status_code=404, detail="Interview session not found")
    if existing_session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    session = complete_interview_session(
        db=db,
        session_id=session_id,
        user_id=current_user.id,
        requested_final_score=payload.final_score,
    )
    if session is None:
        raise HTTPException(status_code=404, detail="Interview session not found")
    return session
