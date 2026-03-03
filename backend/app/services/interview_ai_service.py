from __future__ import annotations
import logging
from typing import Any, TypedDict, cast

from google import genai
from google.genai import types
from pydantic import BaseModel

from app.core.config import INTERVIEW_AI_MODE, GEMINI_API_KEY, GEMINI_MODEL_CHAT
from app.core.constants import InterviewAction, InterviewStage

logger = logging.getLogger(__name__)


class InterviewAIError(RuntimeError):
    pass

class ChatTurn(TypedDict):
    role: str
    content: str

# --- Pydantic Schemas for Strict JSON ---
class InterviewerResponse(BaseModel):
    assistant_message: str
    intent: str
    confidence: str # low, medium, high

class RubricResponse(BaseModel):
    problem_understanding_score: int
    approach_quality_score: int
    code_correctness_reasoning_score: int
    complexity_analysis_score: int
    communication_clarity_score: int
    summary: str


class StageReadinessResponse(BaseModel):
    ready_to_advance: bool
    confidence: str  # low, medium, high
    reason: str


def generate_next_interviewer_message(
    stage: InterviewStage,
    action: InterviewAction,
    recent_messages: list[ChatTurn],
    current_code: str | None = None,
) -> dict[str, Any]:
    fallback = _fallback_interviewer_message(stage=stage, action=action)
    client = _build_client()
    
    if not client:
        logger.error(
            "interview.ai.message.client_unavailable stage=%s action=%s",
            stage,
            action,
        )
        if _is_strict_mode():
            raise InterviewAIError("Gemini client unavailable. Check GEMINI_API_KEY and package setup.")
        return fallback

    system_instruction = (
        "You are a concise technical interviewer. Ask at most one question. "
        "Keep reply under 80 words. Do not provide solutions unless asked."
    )

    # Convert messages to Gemini format (user/model instead of user/assistant)
    contents = []
    for m in recent_messages[-8:]:
        role = "user" if str(m["role"]) == "user" else "model"
        content_text = str(m["content"])
        contents.append(
            types.Content(role=role, parts=[types.Part.from_text(text=content_text)])
        )
    
    # Add the current "hidden" nudge from the engine
    contents.append(types.Content(
        role="user", 
        parts=[types.Part.from_text(text=f"Current stage: {stage}. Action: {action}.")]
    ))
    code_snapshot = _trim_code_context(current_code)
    if code_snapshot:
        contents.append(
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=(
                            "Candidate current code snapshot (may include comments/notes):\n"
                            f"```text\n{code_snapshot}\n```"
                        )
                    )
                ],
            )
        )

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL_CHAT,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.4,
                # This enforces the JSON structure perfectly
                response_mime_type="application/json",
                response_schema=InterviewerResponse,
            ),
        )
        
        # Gemini returns parsed objects directly if response_schema is provided
        parsed = cast(InterviewerResponse | None, response.parsed)
        if parsed is None:
            raise InterviewAIError("Gemini returned no parsed interviewer payload.")
        usage = getattr(response, "usage_metadata", None)
        logger.info(
            "interview.ai.message.success stage=%s action=%s prompt_tokens=%s completion_tokens=%s total_tokens=%s",
            stage,
            action,
            getattr(usage, "prompt_token_count", -1) if usage else -1,
            getattr(usage, "candidates_token_count", -1) if usage else -1,
            getattr(usage, "total_token_count", -1) if usage else -1,
        )
        return {
            "assistant_message": str(parsed.assistant_message),
            "intent": str(parsed.intent or action),
            "confidence": (
                str(parsed.confidence).lower()
                if str(parsed.confidence).lower() in ["low", "medium", "high"]
                else "medium"
            ),
        }
    except Exception as exc:
        logger.exception("interview.ai.message.failure stage=%s action=%s", stage, action)
        if _is_strict_mode():
            raise InterviewAIError(f"Gemini message generation failed: {type(exc).__name__}") from exc
        return fallback


def assess_stage_readiness(
    stage: InterviewStage,
    recent_messages: list[ChatTurn],
    current_code: str | None = None,
) -> dict[str, Any]:
    client = _build_client()
    fallback = {
        "ready_to_advance": False,
        "confidence": "medium",
        "reason": "Fallback readiness assessment used.",
    }
    if not client:
        logger.error("interview.ai.readiness.client_unavailable stage=%s", stage)
        if _is_strict_mode():
            raise InterviewAIError(
                "Gemini client unavailable for readiness assessment."
            )
        return fallback

    system_instruction = (
        "You are evaluating interview stage readiness. "
        "Return JSON only. Be strict: only approve advancement when the candidate has "
        "shown clear understanding for the current stage."
    )
    contents: list[types.Content] = []
    for message in recent_messages[-8:]:
        role = "user" if str(message["role"]) == "user" else "model"
        contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=str(message["content"]))],
            )
        )
    contents.append(
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=(
                        f"Current stage is {stage}. "
                        "Should we move to the next stage now?"
                    )
                )
            ],
        )
    )
    code_snapshot = _trim_code_context(current_code)
    if code_snapshot:
        contents.append(
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=(
                            "Candidate current code snapshot (may include comments/notes):\n"
                            f"```text\n{code_snapshot}\n```"
                        )
                    )
                ],
            )
        )

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL_CHAT,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.1,
                response_mime_type="application/json",
                response_schema=StageReadinessResponse,
            ),
        )
        parsed = cast(StageReadinessResponse | None, response.parsed)
        if parsed is None:
            raise InterviewAIError("Gemini returned no parsed readiness payload.")

        confidence = str(parsed.confidence).lower()
        if confidence not in {"low", "medium", "high"}:
            confidence = "medium"
        usage = getattr(response, "usage_metadata", None)
        logger.info(
            "interview.ai.readiness.success stage=%s ready=%s confidence=%s prompt_tokens=%s completion_tokens=%s total_tokens=%s",
            stage,
            parsed.ready_to_advance,
            confidence,
            getattr(usage, "prompt_token_count", -1) if usage else -1,
            getattr(usage, "candidates_token_count", -1) if usage else -1,
            getattr(usage, "total_token_count", -1) if usage else -1,
        )
        return {
            "ready_to_advance": bool(parsed.ready_to_advance),
            "confidence": confidence,
            "reason": str(parsed.reason).strip()[:300],
        }
    except Exception as exc:
        logger.exception("interview.ai.readiness.failure stage=%s", stage)
        if _is_strict_mode():
            raise InterviewAIError(
                f"Gemini readiness assessment failed: {type(exc).__name__}"
            ) from exc
        return fallback


def evaluate_stage_rubric(
    stage: InterviewStage,
    stage_messages: list[ChatTurn],
    current_code: str | None = None,
) -> dict[str, Any]:
    client = _build_client()
    if not client:
        logger.error("interview.ai.rubric.client_unavailable stage=%s", stage)
        if _is_strict_mode():
            raise InterviewAIError("Gemini client unavailable for rubric evaluation.")
        return _fallback_rubric(stage)

    transcript = "\n".join(
        [f"{str(m['role'])}: {str(m['content'])}" for m in stage_messages[-10:]]
    )
    
    prompt = f"Evaluate the following interview transcript for the stage: {stage}\n\nTranscript:\n{transcript}"
    code_snapshot = _trim_code_context(current_code)
    if code_snapshot:
        prompt += (
            "\n\nCandidate current code snapshot (may include comments/notes):\n"
            f"```text\n{code_snapshot}\n```"
        )

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL_CHAT,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="Evaluate performance. Scores 0-2.",
                response_mime_type="application/json",
                response_schema=RubricResponse,
            ),
        )
        # Convert Pydantic model to dict for your existing frontend/logic
        usage = getattr(response, "usage_metadata", None)
        logger.info(
            "interview.ai.rubric.success stage=%s prompt_tokens=%s completion_tokens=%s total_tokens=%s",
            stage,
            getattr(usage, "prompt_token_count", -1) if usage else -1,
            getattr(usage, "candidates_token_count", -1) if usage else -1,
            getattr(usage, "total_token_count", -1) if usage else -1,
        )
        parsed = cast(RubricResponse | None, response.parsed)
        if parsed is None:
            raise InterviewAIError("Gemini returned no parsed rubric payload.")
        return parsed.model_dump()
    except Exception as exc:
        logger.exception("interview.ai.rubric.failure stage=%s", stage)
        if _is_strict_mode():
            raise InterviewAIError(f"Gemini rubric evaluation failed: {type(exc).__name__}") from exc
        return _fallback_rubric(stage)

def _build_client():
    if not GEMINI_API_KEY:
        return None
    return genai.Client(api_key=GEMINI_API_KEY)

def _fallback_interviewer_message(
    stage: InterviewStage,
    action: InterviewAction,
) -> dict[str, Any]:
    if action == "nudge":
        text = "Take one concrete step. Name your next action and why."
    elif action == "advance":
        prompts = {
            "CLARIFICATION": "Good. What assumptions are you making?",
            "APPROACH_DISCUSSION": "Explain your high-level approach.",
            "PSEUDOCODE": "Give concise pseudocode before coding.",
            "CODING": "Implement now and explain key choices.",
            "COMPLEXITY_DISCUSSION": "State time and space complexity.",
            "FOLLOW_UP": "How would you adapt to a stricter constraint?",
            "FEEDBACK": "Give a short self-review of your performance.",
            "COMPLETE": "Interview complete. Nice work.",
            "INTRO": "Please restate the problem and ask one clarification.",
        }
        text = prompts.get(stage, "Continue.")
    elif action == "stay":
        text = "Interview is complete."
    else:
        text = "Can you elaborate in one or two concise points?"

    return {
        "assistant_message": text,
        "intent": action,
        "confidence": "medium",
    }


def _fallback_rubric(stage: InterviewStage) -> dict[str, Any]:
    _ = stage
    return {
        "problem_understanding_score": 0,
        "approach_quality_score": 0,
        "code_correctness_reasoning_score": 0,
        "complexity_analysis_score": 0,
        "communication_clarity_score": 0,
        "summary": "Automatic rubric fallback used (LLM unavailable).",
    }


def _normalize_rubric(raw: dict[str, Any]) -> dict[str, Any]:
    def score(key: str) -> int:
        value = raw.get(key, 0)
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            parsed = 0
        return max(0, min(2, parsed))

    return {
        "problem_understanding_score": score("problem_understanding_score"),
        "approach_quality_score": score("approach_quality_score"),
        "code_correctness_reasoning_score": score("code_correctness_reasoning_score"),
        "complexity_analysis_score": score("complexity_analysis_score"),
        "communication_clarity_score": score("communication_clarity_score"),
        "summary": str(raw.get("summary", "")).strip()[:500],
    }


def _extract_usage(completion: Any) -> dict[str, int]:
    usage = getattr(completion, "usage", None)
    if usage is None:
        return {"prompt_tokens": -1, "completion_tokens": -1, "total_tokens": -1}

    if isinstance(usage, dict):
        prompt_tokens = int(usage.get("prompt_tokens", -1))
        completion_tokens = int(usage.get("completion_tokens", -1))
        total_tokens = int(usage.get("total_tokens", -1))
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
        }

    return {
        "prompt_tokens": int(getattr(usage, "prompt_tokens", -1)),
        "completion_tokens": int(getattr(usage, "completion_tokens", -1)),
        "total_tokens": int(getattr(usage, "total_tokens", -1)),
    }


def _is_strict_mode() -> bool:
    return INTERVIEW_AI_MODE == "strict"


def _trim_code_context(current_code: str | None, limit: int = 12000) -> str:
    if not current_code:
        return ""
    trimmed = current_code.strip()
    if len(trimmed) <= limit:
        return trimmed
    return trimmed[:limit] + "\n...<truncated>..."
