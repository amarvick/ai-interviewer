# TODO - break down into other services AND revisit when experimenting
from __future__ import annotations

from dataclasses import dataclass

from app.core.constants import InterviewAction, InterviewStage

MAX_NUDGES_PER_STAGE = 2
MAX_TURNS_BEFORE_SOFT_ADVANCE = 4
SHORT_REPLY_WORD_THRESHOLD = 4

ADVANCE_ORDER: dict[InterviewStage, InterviewStage] = {
    "INTRO": "CLARIFICATION",
    "CLARIFICATION": "APPROACH_DISCUSSION",
    "APPROACH_DISCUSSION": "PSEUDOCODE",
    "PSEUDOCODE": "CODING",
    "CODING": "COMPLEXITY_DISCUSSION",
    "COMPLEXITY_DISCUSSION": "FOLLOW_UP",
    "FOLLOW_UP": "FEEDBACK",
    "FEEDBACK": "COMPLETE",
    "COMPLETE": "COMPLETE",
}


@dataclass
class StageDecision:
    next_stage: InterviewStage
    action: InterviewAction
    should_score_stage: bool
    stuck_signal_count: int
    nudge_reason: str | None = None


def decide_stage_transition(
    current_stage: InterviewStage,
    latest_user_message: str,
    turn_count_in_stage: int,
    stuck_signal_count: int,
    nudges_used_in_stage: int,
    has_submission: bool = False,
) -> StageDecision:
    """
    Deterministic transition logic for interview session stages.
    - Keeps stage transitions server-controlled.
    - Triggers nudge actions when user appears stuck.
    """
    if current_stage == "COMPLETE":
        return StageDecision(
            next_stage="COMPLETE",
            action="stay",
            should_score_stage=False,
            stuck_signal_count=stuck_signal_count,
        )

    text = (latest_user_message or "").strip().lower()
    ambiguous = _is_ambiguous_reply(text)
    new_stuck_count = stuck_signal_count + 1 if ambiguous else 0

    if (
        ambiguous
        and nudges_used_in_stage < MAX_NUDGES_PER_STAGE
        and current_stage not in {"FEEDBACK", "COMPLETE"}
    ):
        return StageDecision(
            next_stage=current_stage,
            action="nudge",
            should_score_stage=False,
            stuck_signal_count=new_stuck_count,
            nudge_reason="short_or_unclear_response",
        )

    should_advance = _should_advance(
        stage=current_stage,
        text=text,
        turn_count_in_stage=turn_count_in_stage,
        has_submission=has_submission,
    )

    if should_advance:
        return StageDecision(
            next_stage=ADVANCE_ORDER[current_stage],
            action="advance",
            should_score_stage=current_stage
            in {
                "CLARIFICATION",
                "APPROACH_DISCUSSION",
                "PSEUDOCODE",
                "CODING",
                "COMPLEXITY_DISCUSSION",
                "FOLLOW_UP",
                "FEEDBACK",
            },
            stuck_signal_count=0,
        )

    return StageDecision(
        next_stage=current_stage,
        action="ask_question",
        should_score_stage=False,
        stuck_signal_count=new_stuck_count,
    )


def _is_ambiguous_reply(text: str) -> bool:
    if not text:
        return True

    word_count = len([word for word in text.split() if word.strip()])
    if word_count <= SHORT_REPLY_WORD_THRESHOLD:
        return True

    ambiguous_markers = {
        "idk",
        "don't know",
        "not sure",
        "no idea",
        "stuck",
        "help",
        "hmm",
        "unsure",
        "uhh"
    }
    return any(marker in text for marker in ambiguous_markers)


def _should_advance(
    stage: InterviewStage,
    text: str,
    turn_count_in_stage: int,
    has_submission: bool,
) -> bool:
    if stage == "CODING":
        return has_submission

    if stage == "FOLLOW_UP":
        return turn_count_in_stage >= 2 or _contains_any(
            text, {"tradeoff", "alternative", "edge case", "optimiz"}
        )

    if stage == "FEEDBACK":
        return turn_count_in_stage >= 1

    stage_keywords: dict[InterviewStage, set[str]] = {
        "INTRO": {"understand", "problem", "clarify", "question"},
        "CLARIFICATION": {"assume", "constraint", "input", "output", "edge"},
        "APPROACH_DISCUSSION": {"hash", "two pointer", "plan", "approach", "iterate"},
        "PSEUDOCODE": {"pseudo", "step", "loop", "if", "return"},
        "COMPLEXITY_DISCUSSION": {"o(", "time", "space", "complexity", "o of"},
        "COMPLETE": set(),
        "CODING": set(),
        "FOLLOW_UP": set(),
        "FEEDBACK": set(),
    }

    if _contains_any(text, stage_keywords[stage]):
        return True

    return turn_count_in_stage >= MAX_TURNS_BEFORE_SOFT_ADVANCE


def _contains_any(text: str, markers: set[str]) -> bool:
    return any(marker in text for marker in markers)
