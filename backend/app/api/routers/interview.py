from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
from time import perf_counter

from app.core.auth import get_current_user
from app.db.database import get_db
from app.db.models.user import User
from app.schemas.interview import (
    InterviewCompletionResponse,
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
from app.services.interview_ai_service import InterviewAIError
from app.crud.interview import get_interview_session_by_id

router = APIRouter(prefix="/interview", tags=["interview"])
logger = logging.getLogger(__name__)


@router.post("/session/start", response_model=InterviewSessionResponse)
def create_interview_session(
    payload: InterviewSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start_time = perf_counter()
    session = start_interview_session(
        db=db,
        user_id=current_user.id,
        problem_id=payload.problem_id,
    )
    if session is None:
        logger.warning(
            "interview.start.failed user_id=%s problem_id=%s reason=problem_not_found",
            current_user.id,
            payload.problem_id,
        )
        raise HTTPException(status_code=404, detail="Problem not found")
    latency_ms = int((perf_counter() - start_time) * 1000)
    logger.info(
        "interview.start.success user_id=%s session_id=%s problem_id=%s latency_ms=%s",
        current_user.id,
        session.id,
        payload.problem_id,
        latency_ms,
    )
    return session


@router.get("/session/{session_id}", response_model=InterviewSessionDetailResponse)
def get_interview_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start_time = perf_counter()
    session = get_interview_session_by_id(db, session_id)
    if session is None:
        logger.warning(
            "interview.get.failed user_id=%s session_id=%s reason=not_found",
            current_user.id,
            session_id,
        )
        raise HTTPException(status_code=404, detail="Interview session not found")
    if session.user_id != current_user.id:
        logger.warning(
            "interview.get.forbidden user_id=%s session_id=%s owner_user_id=%s",
            current_user.id,
            session_id,
            session.user_id,
        )
        raise HTTPException(status_code=403, detail="Forbidden")
    latency_ms = int((perf_counter() - start_time) * 1000)
    logger.info(
        "interview.get.success user_id=%s session_id=%s stage=%s latency_ms=%s",
        current_user.id,
        session_id,
        session.stage,
        latency_ms,
    )
    return session


@router.post("/session/{session_id}/message", response_model=InterviewSessionDetailResponse)
def post_interview_message(
    session_id: str,
    payload: InterviewMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start_time = perf_counter()
    existing_session = get_interview_session_by_id(db, session_id)
    if existing_session is None:
        logger.warning(
            "interview.message.failed user_id=%s session_id=%s reason=not_found",
            current_user.id,
            session_id,
        )
        raise HTTPException(status_code=404, detail="Interview session not found")
    if existing_session.user_id != current_user.id:
        logger.warning(
            "interview.message.forbidden user_id=%s session_id=%s owner_user_id=%s",
            current_user.id,
            session_id,
            existing_session.user_id,
        )
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        session = process_interview_message(
            db=db,
            session_id=session_id,
            user_id=current_user.id,
            content=payload.content,
            has_submission=payload.has_submission,
            current_code=payload.current_code,
            chat_history=payload.chat_history,
        )
    except InterviewAIError as exc:
        logger.warning(
            "interview.message.ai_failure user_id=%s session_id=%s detail=%s",
            current_user.id,
            session_id,
            str(exc),
        )
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if session is None:
        logger.warning(
            "interview.message.failed user_id=%s session_id=%s reason=process_failed",
            current_user.id,
            session_id,
        )
        raise HTTPException(status_code=404, detail="Interview session not found")
    latency_ms = int((perf_counter() - start_time) * 1000)
    stage = session.get("stage") if isinstance(session, dict) else session.stage
    logger.info(
        "interview.message.success user_id=%s session_id=%s stage=%s latency_ms=%s",
        current_user.id,
        session_id,
        stage,
        latency_ms,
    )
    return session


@router.post("/session/{session_id}/complete", response_model=InterviewCompletionResponse)
def complete_session(
    session_id: str,
    payload: InterviewSessionComplete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start_time = perf_counter()
    existing_session = get_interview_session_by_id(db, session_id)
    if existing_session is None:
        logger.warning(
            "interview.complete.failed user_id=%s session_id=%s reason=not_found",
            current_user.id,
            session_id,
        )
        raise HTTPException(status_code=404, detail="Interview session not found")
    if existing_session.user_id != current_user.id:
        logger.warning(
            "interview.complete.forbidden user_id=%s session_id=%s owner_user_id=%s",
            current_user.id,
            session_id,
            existing_session.user_id,
        )
        raise HTTPException(status_code=403, detail="Forbidden")

    session = complete_interview_session(
        db=db,
        session_id=session_id,
        user_id=current_user.id,
        requested_final_score=payload.final_score,
    )
    if session is None:
        logger.warning(
            "interview.complete.failed user_id=%s session_id=%s reason=process_failed",
            current_user.id,
            session_id,
        )
        raise HTTPException(status_code=404, detail="Interview session not found")
    latency_ms = int((perf_counter() - start_time) * 1000)
    logger.info(
        "interview.complete.success user_id=%s session_id=%s final_score=%s latency_ms=%s",
        current_user.id,
        session_id,
        session.get("final_score"),
        latency_ms,
    )
    return session
