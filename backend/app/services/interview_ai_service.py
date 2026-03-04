from __future__ import annotations
import logging
from typing import Any, TypedDict, cast

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from app.core.config import INTERVIEW_AI_MODE, GEMINI_API_KEY, GEMINI_MODEL_CHAT

logger = logging.getLogger(__name__)

class InterviewAIError(RuntimeError):
    pass

class ChatTurn(TypedDict):
    role: str
    content: str

# TODO - put these in schemas

class InterviewChecklist(BaseModel):
    clarified_constraints: bool = Field(description="User understands input/output and edge cases")
    proposed_approach: bool = Field(description="User explained the high-level logic and algorithm")
    complexity_analyzed: bool = Field(description="User discussed Big-O Time and Space complexity")
    ready_to_code: bool = Field(description="Set to true ONLY when all above are True")

class InterviewerResponse(BaseModel):
    assistant_message: str = Field(description="The text shown to the candidate")
    checklist_status: InterviewChecklist
    internal_thought: str = Field(description="Your reasoning for why you are asking this specific question")
    confidence: str # low, medium, high

class RubricResponse(BaseModel):
    problem_understanding_score: int
    approach_quality_score: int
    code_correctness_reasoning_score: int
    complexity_analysis_score: int
    communication_clarity_score: int
    summary: str

def generate_next_interviewer_message(
    recent_messages: list[ChatTurn],
    current_code: str | None = None,
) -> dict[str, Any]:
    client = _build_client()
    if not client:
        if _is_strict_mode(): raise InterviewAIError("Gemini API key missing.")
        return _fallback_interviewer_message()

    system_instruction = (
        "You are an elite Technical Interviewer. Guide the candidate through a LeetCode interview.\n\n"
        "GOAL: Ensure the candidate explains the problem, edge cases, and complexity BEFORE they start coding.\n"
        "RULES:\n"
        "1. PROACTIVITY: If they code too early, ask them to discuss complexity first.\n"
        "2. CONCISENESS: Keep responses under 60 words.\n"
        "3. STATE: Update the 'checklist_status' based on the history.\n"
        "4. NO SPOILERS: Never provide the full solution code."
    )

    contents = _prepare_contents(recent_messages, current_code)

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL_CHAT,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.4,
                response_mime_type="application/json",
                response_schema=InterviewerResponse,
            ),
        )
        
        parsed = cast(InterviewerResponse, response.parsed)
        _log_usage(response, "interview_chat")

        return {
            "assistant_message": parsed.assistant_message,
            "checklist": parsed.checklist_status.model_dump(),
            "can_code": parsed.checklist_status.ready_to_code,
            "internal_thought": parsed.internal_thought
        }
    except Exception as exc:
        logger.exception("Gemini error")
        if _is_quota_error(exc):
            raise InterviewAIError(
                "AI quota exceeded. Please check your Gemini billing/quota and try again."
            ) from exc
        if _is_strict_mode():
            raise InterviewAIError(
                f"Gemini message generation failed: {type(exc).__name__}"
            ) from exc
        return _fallback_interviewer_message()

def evaluate_stage_rubric(
    stage_messages: list[ChatTurn],
    current_code: str | None = None,
) -> dict[str, Any]:
    client = _build_client()
    if not client: return _fallback_rubric()

    transcript = "\n".join([f"{m['role']}: {m['content']}" for m in stage_messages])
    code_context = f"\n\nCode Snapshot:\n{current_code}" if current_code else ""

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL_CHAT,
            contents=f"Review this transcript and code:\n{transcript}{code_context}",
            config=types.GenerateContentConfig(
                system_instruction="Score 0-2 for each category. Provide a fair, 2-sentence summary.",
                response_mime_type="application/json",
                response_schema=RubricResponse,
            ),
        )
        return cast(RubricResponse, response.parsed).model_dump()
    except Exception as exc:
        if _is_quota_error(exc):
            raise InterviewAIError(
                "AI quota exceeded. Please check your Gemini billing/quota and try again."
            ) from exc
        if _is_strict_mode():
            raise InterviewAIError(
                f"Gemini rubric evaluation failed: {type(exc).__name__}"
            ) from exc
        return _fallback_rubric()

def _prepare_contents(messages: list[ChatTurn], code: str | None) -> list[types.Content]:
    contents = []
    for m in messages[-10:]:
        role = "user" if m["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=m["content"])]))
    
    if code:
        contents.append(types.Content(
            role="user",
            parts=[types.Part.from_text(text=f"SYSTEM NOTE: Current Code State:\n{code[:5000]}")]
        ))
    return contents

def _build_client():
    return genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

def _log_usage(response: Any, label: str):
    usage = getattr(response, "usage_metadata", None)
    if usage:
        logger.info(f"Gemini Usage [{label}]: {usage.total_token_count} tokens")

def _is_strict_mode() -> bool:
    return INTERVIEW_AI_MODE == "strict"


def _is_quota_error(exc: Exception) -> bool:
    text = str(exc).lower()
    markers = (
        "quota",
        "resource_exhausted",
        "rate limit",
        "429",
        "insufficient",
        "billing",
    )
    return any(marker in text for marker in markers)

def _fallback_interviewer_message() -> dict[str, Any]:
    return {
        "assistant_message": "Tell me more about your approach.",
        "checklist": {"clarified_constraints": False, "proposed_approach": False, "complexity_analyzed": False, "ready_to_code": False},
        "can_code": False
    }

def _fallback_rubric() -> dict[str, Any]:
    return {
        "problem_understanding_score": 0, "approach_quality_score": 0,
        "code_correctness_reasoning_score": 0, "complexity_analysis_score": 0,
        "communication_clarity_score": 0, "summary": "Evaluation failed."
    }
