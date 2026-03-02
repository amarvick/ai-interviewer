from __future__ import annotations
import json
import logging
from time import perf_counter
from typing import Any

# Import the new Google GenAI SDK
from google import genai
from google.genai import types
from pydantic import BaseModel

from app.core.config import INTERVIEW_AI_MODE, GEMINI_API_KEY, GEMINI_MODEL
from app.core.constants import InterviewAction, InterviewStage

logger = logging.getLogger(__name__)

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

def generate_next_interviewer_message(
    stage: InterviewStage,
    action: InterviewAction,
    recent_messages: list[dict[str, str]],
) -> dict[str, Any]:
    start_time = perf_counter()
    fallback = _fallback_interviewer_message(stage=stage, action=action)
    client = _build_client()
    
    if not client:
        if _is_strict_mode(): raise RuntimeError("Gemini Client Unavailable")
        return fallback

    system_instruction = (
        "You are a concise technical interviewer. Ask at most one question. "
        "Keep reply under 80 words. Do not provide solutions unless asked."
    )

    # Convert messages to Gemini format (user/model instead of user/assistant)
    contents = []
    for m in recent_messages[-8:]:
        role = "user" if m["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=m["content"])]))
    
    # Add the current "hidden" nudge from the engine
    contents.append(types.Content(
        role="user", 
        parts=[types.Part.from_text(text=f"Current stage: {stage}. Action: {action}.")]
    ))

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
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
        parsed = response.parsed
        return {
            "assistant_message": parsed.assistant_message,
            "intent": parsed.intent or action,
            "confidence": parsed.confidence.lower() if parsed.confidence in ["low", "medium", "high"] else "medium"
        }
    except Exception as exc:
        logger.exception("Gemini failed")
        return fallback

def evaluate_stage_rubric(
    stage: InterviewStage,
    stage_messages: list[dict[str, str]],
) -> dict[str, Any]:
    client = _build_client()
    if not client: return _fallback_rubric(stage)

    transcript = "\n".join([f"{m['role']}: {m['content']}" for m in stage_messages[-10:]])
    
    prompt = f"Evaluate the following interview transcript for the stage: {stage}\n\nTranscript:\n{transcript}"

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="Evaluate performance. Scores 0-2.",
                response_mime_type="application/json",
                response_schema=RubricResponse,
            ),
        )
        # Convert Pydantic model to dict for your existing frontend/logic
        return response.parsed.model_dump()
    except Exception:
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
