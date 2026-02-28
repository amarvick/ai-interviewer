from datetime import datetime
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


def start_interview_session(db, user_id: str, problem_id: str):
    problem = get_problem_by_id(db, problem_id)
    if problem is None:
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
        stage_at_message=session.stage,
        user_id=None,
    )
    db.commit()
    return get_interview_session_by_id(db, session.id)


def process_interview_message(
    db,
    session_id: str,
    user_id: str,
    content: str,
    has_submission: bool,
):
    session = get_interview_session_by_id(db, session_id)
    if session is None:
        return None
    if session.status == "COMPLETED":
        return session

    create_interview_message(
        db=db,
        session_id=session.id,
        user_id=user_id,
        role="user",
        content=content,
        stage_at_message=session.stage,
    )

    session = get_interview_session_by_id(db, session_id)
    if session is None:
        return None

    current_stage: InterviewStage = session.stage
    user_turns_in_stage = sum(
        1
        for message in session.messages
        if message.role == "user" and message.stage_at_message == current_stage
    )
    decision = decide_stage_transition(
        current_stage=current_stage,
        latest_user_message=content,
        turn_count_in_stage=user_turns_in_stage,
        stuck_signal_count=session.stuck_signal_count,
        nudges_used_in_stage=session.nudges_used_in_stage,
        has_submission=has_submission,
    )

    previous_stage = session.stage
    session.stage = decision.next_stage
    session.stuck_signal_count = decision.stuck_signal_count

    if decision.action == "nudge":
        session.nudges_used_in_stage += 1
    elif decision.action == "advance":
        session.nudges_used_in_stage = 0
    elif decision.action == "stay":
        session.nudges_used_in_stage = session.nudges_used_in_stage

    if decision.next_stage == "COMPLETE":
        session.status = "COMPLETED"
        session.completed_at = datetime.utcnow()

    if decision.should_score_stage:
        stage_messages = [
            {"role": message.role, "content": message.content}
            for message in session.messages
            if message.stage_at_message == previous_stage
        ]
        rubric = evaluate_stage_rubric(stage=previous_stage, stage_messages=stage_messages)
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

    ai_message_payload = generate_next_interviewer_message(
        action=decision.action,
        stage=decision.next_stage,
        recent_messages=_build_recent_context(db, session.id),
    )
    create_interview_message(
        db=db,
        session_id=session.id,
        role="assistant",
        content=ai_message_payload["assistant_message"],
        stage_at_message=session.stage,
        user_id=None,
    )

    db.commit()
    return get_interview_session_by_id(db, session.id)


def complete_interview_session(
    db,
    session_id: str,
    user_id: str,
    requested_final_score: float | None = None,
):
    session = get_interview_session_by_id(db, session_id)
    if session is None:
        return None
    if session.user_id != user_id:
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
    session.stage = "COMPLETE"
    session.completed_at = datetime.utcnow()
    db.commit()
    return get_interview_session_by_id(db, session.id)


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
