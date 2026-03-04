from datetime import datetime
import logging
from time import perf_counter
from typing import Any, cast
from app.core.constants import InterviewStage
from app.crud.interview import (
    create_interview_evaluation,
    create_interview_message,
    create_interview_session,
    get_interview_session_by_id,
    get_recent_evaluations_by_session_id,
    get_recent_messages_by_session_id,
)
from app.crud.problem import get_problem_by_id
from app.services.interview_stage_engine import decide_stage_transition
from app.services.interview_ai_service import (
    evaluate_stage_rubric,
    generate_next_interviewer_message,
)

logger = logging.getLogger(__name__)


def _as_stage(value: Any) -> InterviewStage:
    stage = str(value)
    valid: set[str] = {
        "INTRO",
        "CLARIFICATION",
        "APPROACH_DISCUSSION",
        "PSEUDOCODE",
        "CODING",
        "COMPLEXITY_DISCUSSION",
        "FOLLOW_UP",
        "FEEDBACK",
        "COMPLETE",
    }
    if stage not in valid:
        return "INTRO"
    return cast(InterviewStage, stage)


def start_interview_session(db, user_id: str, problem_id: str):
    start_time = perf_counter()
    problem = get_problem_by_id(db, problem_id)
    if problem is None:
        logger.warning(
            "interview.service.start.problem_not_found user_id=%s problem_id=%s",
            user_id,
            problem_id,
        )
        return None

    session = create_interview_session(db, user_id=user_id, problem_id=problem_id)
    create_interview_message(
        db=db,
        session_id=session.id,
        role="assistant",
        content=(
            "Welcome to the interview. Briefly restate the problem in your own words "
            "and ask one clarifying question."
        ),
        stage_at_message=_as_stage(session.stage),
        user_id=None,
    )
    db.commit()
    logger.info(
        "interview.service.start.created user_id=%s session_id=%s problem_id=%s latency_ms=%s",
        user_id,
        session.id,
        problem_id,
        int((perf_counter() - start_time) * 1000),
    )
    return get_interview_session_by_id(db, session.id)


def process_interview_message(
    db,
    session_id: str,
    user_id: str,
    content: str,
    has_submission: bool,
    current_code: str | None = None,
    chat_history: list[dict[str, str]] | None = None,
):
    start_time = perf_counter()
    session = get_interview_session_by_id(db, session_id)
    if session is None:
        logger.warning(
            "interview.service.message.not_found session_id=%s user_id=%s",
            session_id,
            user_id,
        )
        return None
    if session.status == "COMPLETED":
        logger.info(
            "interview.service.message.already_completed session_id=%s user_id=%s",
            session_id,
            user_id,
        )
        return session

    create_interview_message(
        db=db,
        session_id=session.id,
        user_id=user_id,
        role="user",
        content=content,
        stage_at_message=_as_stage(session.stage),
    )

    session = get_interview_session_by_id(db, session_id)
    if session is None:
        return None

    current_stage: InterviewStage = _as_stage(session.stage)
    user_turns_in_stage = sum(
        1
        for message in session.messages
        if str(message.role) == "user"
        and _as_stage(message.stage_at_message) == current_stage
    )
    decision = decide_stage_transition(
        current_stage=current_stage,
        latest_user_message=content,
        turn_count_in_stage=user_turns_in_stage,
        stuck_signal_count=session.stuck_signal_count,
        nudges_used_in_stage=session.nudges_used_in_stage,
        has_submission=has_submission,
    )
    effective_decision = decision

    previous_stage: InterviewStage = _as_stage(session.stage)
    setattr(session, "stage", effective_decision.next_stage)
    session.stuck_signal_count = effective_decision.stuck_signal_count

    if effective_decision.action == "nudge":
        session.nudges_used_in_stage += 1
    elif effective_decision.action == "advance":
        session.nudges_used_in_stage = 0
    elif effective_decision.action == "stay":
        session.nudges_used_in_stage = session.nudges_used_in_stage

    if effective_decision.next_stage == "COMPLETE":
        session.status = "COMPLETED"
        session.completed_at = datetime.utcnow()

    logger.info(
        "interview.stage.transition session_id=%s user_id=%s from_stage=%s to_stage=%s action=%s "
        "turns_in_stage=%s stuck_signals=%s nudges_used=%s score_stage=%s has_submission=%s",
        session.id,
        user_id,
        previous_stage,
        effective_decision.next_stage,
        effective_decision.action,
        user_turns_in_stage,
        session.stuck_signal_count,
        session.nudges_used_in_stage,
        effective_decision.should_score_stage,
        has_submission,
    )

    if effective_decision.should_score_stage:
        stage_messages = [
            {"role": message.role, "content": message.content}
            for message in session.messages
            if _as_stage(message.stage_at_message) == previous_stage
        ]
        rubric = evaluate_stage_rubric(
            stage_messages=stage_messages,
            current_code=current_code,
        )
        category_total = (
            rubric["problem_understanding_score"]
            + rubric["approach_quality_score"]
            + rubric["code_correctness_reasoning_score"]
            + rubric["complexity_analysis_score"]
            + rubric["communication_clarity_score"]
        )
        create_interview_evaluation(
            db=db,
            session_id=session.id,
            stage=previous_stage,
            summary=rubric.get("summary", f"Stage {previous_stage} evaluation complete."),
            problem_understanding_score=rubric["problem_understanding_score"],
            approach_quality_score=rubric["approach_quality_score"],
            code_correctness_reasoning_score=rubric["code_correctness_reasoning_score"],
            complexity_analysis_score=rubric["complexity_analysis_score"],
            communication_clarity_score=rubric["communication_clarity_score"],
            total_score=category_total,
            passed=category_total >= 6,
            rubric_json={"source": "llm_eval", "stage": previous_stage, **rubric},
        )

    full_history = _normalize_chat_history(chat_history)
    ai_context = full_history if full_history else _build_recent_context(db, session.id)
    ai_message_payload = generate_next_interviewer_message(
        recent_messages=ai_context,
        current_code=current_code,
    )
    create_interview_message(
        db=db,
        session_id=session.id,
        role="assistant",
        content=ai_message_payload["assistant_message"],
        stage_at_message=_as_stage(session.stage),
        user_id=None,
    )

    db.commit()
    logger.info(
        "interview.service.message.completed session_id=%s user_id=%s stage=%s latency_ms=%s",
        session.id,
        user_id,
        session.stage,
        int((perf_counter() - start_time) * 1000),
    )
    refreshed = get_interview_session_by_id(db, session.id)
    if refreshed is None:
        return None
    return _serialize_session_detail(
        refreshed,
        can_code=bool(ai_message_payload.get("can_code", False)),
    )


def complete_interview_session(
    db,
    session_id: str,
    user_id: str,
    requested_final_score: float | None = None,
):
    start_time = perf_counter()
    session = get_interview_session_by_id(db, session_id)
    if session is None:
        logger.warning(
            "interview.service.complete.not_found session_id=%s user_id=%s",
            session_id,
            user_id,
        )
        return None
    if session.user_id != user_id:
        logger.warning(
            "interview.service.complete.forbidden session_id=%s user_id=%s owner_user_id=%s",
            session_id,
            user_id,
            session.user_id,
        )
        return None

    evaluations = get_recent_evaluations_by_session_id(db, session.id, limit=500)
    computed_score = requested_final_score
    if computed_score is None:
        if evaluations:
            computed_score = sum(e.total_score for e in evaluations) / len(evaluations)
        else:
            computed_score = 0

    session.final_score = round(float(computed_score), 2)
    session.status = "COMPLETED"
    setattr(session, "stage", "COMPLETE")
    session.completed_at = datetime.utcnow()
    db.commit()
    refreshed = get_interview_session_by_id(db, session.id)
    if refreshed is None:
        return None
    feedback = _build_final_feedback(evaluations)
    logger.info(
        "interview.service.complete.completed session_id=%s user_id=%s final_score=%s eval_count=%s latency_ms=%s",
        session.id,
        user_id,
        session.final_score,
        len(evaluations),
        int((perf_counter() - start_time) * 1000),
    )
    return {
        "id": refreshed.id,
        "user_id": refreshed.user_id,
        "problem_id": refreshed.problem_id,
        "stage": _as_stage(refreshed.stage),
        "status": refreshed.status,
        "final_score": refreshed.final_score,
        "stuck_signal_count": refreshed.stuck_signal_count,
        "nudges_used_in_stage": refreshed.nudges_used_in_stage,
        "started_at": refreshed.started_at,
        "completed_at": refreshed.completed_at,
        "created_at": refreshed.created_at,
        "updated_at": refreshed.updated_at,
        "strengths": feedback["strengths"],
        "gaps": feedback["gaps"],
        "next_steps": feedback["next_steps"],
    }


def _build_recent_context(db, session_id: str) -> list[dict[str, str]]:
    recent_messages = get_recent_messages_by_session_id(db, session_id, limit=8)
    recent_messages = list(reversed(recent_messages))
    recent_evaluations = get_recent_evaluations_by_session_id(db, session_id, limit=3)

    context: list[dict[str, str]] = [
        {"role": message.role, "content": message.content}
        for message in recent_messages
    ]
    if recent_evaluations:
        summary_lines = [
            f"{evaluation.stage}: {evaluation.summary or 'No summary'}"
            for evaluation in reversed(recent_evaluations)
        ]
        context.insert(
            0,
            {
                "role": "system",
                "content": "Recent evaluation summaries:\n" + "\n".join(summary_lines),
            },
        )
    return context


def _normalize_chat_history(
    chat_history: list[dict[str, str]] | None,
) -> list[dict[str, str]]:
    if not chat_history:
        return []
    normalized: list[dict[str, str]] = []
    for turn in chat_history:
        role = str(turn.get("role", "")).strip().lower()
        content = str(turn.get("content", "")).strip()
        if role not in {"user", "assistant", "system"} or not content:
            continue
        normalized.append({"role": role, "content": content})
    return normalized


def _serialize_session_detail(session, can_code: bool) -> dict[str, Any]:
    return {
        "id": session.id,
        "user_id": session.user_id,
        "problem_id": session.problem_id,
        "stage": _as_stage(session.stage),
        "status": session.status,
        "final_score": session.final_score,
        "stuck_signal_count": session.stuck_signal_count,
        "nudges_used_in_stage": session.nudges_used_in_stage,
        "started_at": session.started_at,
        "completed_at": session.completed_at,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "messages": session.messages,
        "evaluations": session.evaluations,
        "can_code": can_code,
    }


def _build_final_feedback(evaluations: list) -> dict[str, list[str]]:
    if not evaluations:
        return {
            "strengths": ["You completed the interview flow."],
            "gaps": ["Not enough rubric data yet to identify specific gaps."],
            "next_steps": [
                "Complete another interview run with fuller explanations per stage."
            ],
        }

    category_totals = {
        "problem_understanding": 0.0,
        "approach_quality": 0.0,
        "code_correctness_reasoning": 0.0,
        "complexity_analysis": 0.0,
        "communication_clarity": 0.0,
    }
    for evaluation in evaluations:
        category_totals["problem_understanding"] += evaluation.problem_understanding_score
        category_totals["approach_quality"] += evaluation.approach_quality_score
        category_totals["code_correctness_reasoning"] += (
            evaluation.code_correctness_reasoning_score
        )
        category_totals["complexity_analysis"] += evaluation.complexity_analysis_score
        category_totals["communication_clarity"] += evaluation.communication_clarity_score

    count = float(len(evaluations))
    category_averages = {key: value / count for key, value in category_totals.items()}
    ordered_best = sorted(category_averages.items(), key=lambda item: item[1], reverse=True)
    ordered_worst = sorted(category_averages.items(), key=lambda item: item[1])

    label = {
        "problem_understanding": "Problem understanding",
        "approach_quality": "Approach quality",
        "code_correctness_reasoning": "Correctness reasoning",
        "complexity_analysis": "Complexity analysis",
        "communication_clarity": "Communication clarity",
    }
    next_step_by_gap = {
        "problem_understanding": "Restate requirements and list at least 3 edge cases before coding.",
        "approach_quality": "Compare one alternative approach and justify your final choice.",
        "code_correctness_reasoning": "Explain one invariant and walk through one concrete test trace.",
        "complexity_analysis": "State exact time/space Big-O and tie it to each major operation.",
        "communication_clarity": "Answer in short structured bullets: plan, why, tradeoff.",
    }

    strengths = [f"{label[key]} ({avg:.2f}/2)" for key, avg in ordered_best[:2]]
    gap_candidates = [item for item in ordered_worst if item[1] < 1.5] or ordered_worst[:2]
    gaps = [f"{label[key]} ({avg:.2f}/2)" for key, avg in gap_candidates[:2]]
    next_steps = [next_step_by_gap[key] for key, _ in gap_candidates[:3]]

    return {"strengths": strengths, "gaps": gaps, "next_steps": next_steps}
