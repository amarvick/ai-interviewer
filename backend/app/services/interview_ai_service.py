from __future__ import annotations

import json
from typing import Any
import logging
from time import perf_counter

from app.core.config import OPENAI_API_KEY, OPENAI_MODEL
from app.core.constants import InterviewAction, InterviewStage

from openai import OpenAI

logger = logging.getLogger(__name__)

def generate_next_interviewer_message(
    stage: InterviewStage,
    action: InterviewAction,
    recent_messages: list[dict[str, str]],
) -> dict[str, Any]:
    """
    Returns JSON-friendly interviewer output:
    {
      "assistant_message": str,
      "intent": str,
      "confidence": "low" | "medium" | "high"
    }
    """
    
    start_time = perf_counter()
    fallback = _fallback_interviewer_message(stage=stage, action=action)
    client = _build_client()
    
    if client is None:
        logger.info(
            "interview.ai.message.fallback reason=client_unavailable stage=%s action=%s",
            stage,
            action,
        )
        return fallback

    system_prompt = (
        "You are a concise technical interviewer. "
        "Ask at most one question. Keep reply under 80 words. "
        "Do not provide full solutions unless explicitly asked. "
        "Return strict JSON with keys: assistant_message, intent, confidence."
    )

    payload_messages = [{"role": "system", "content": system_prompt}]
    payload_messages.extend(
        {"role": message["role"], "content": message["content"]}
        for message in recent_messages[-8:]
        if "role" in message and "content" in message
    )
    payload_messages.append(
        {
            "role": "system",
            "content": (
                f"Current stage: {stage}. Stage-engine action: {action}. "
                "Shape the next interviewer turn accordingly."
            ),
        }
    )

    try:
        completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=payload_messages,
            response_format={"type": "json_object"},
            temperature=0.4,
        )
        content = completion.choices[0].message.content or "{}"
        parsed = json.loads(content)
        assistant_message = str(parsed.get("assistant_message", "")).strip()
        intent = str(parsed.get("intent", action)).strip() or action
        confidence = str(parsed.get("confidence", "medium")).strip().lower()
        if confidence not in {"low", "medium", "high"}:
            confidence = "medium"
        if not assistant_message:
            logger.warning(
                "interview.ai.message.empty_content stage=%s action=%s latency_ms=%s",
                stage,
                action,
                int((perf_counter() - start_time) * 1000),
            )
            return fallback
        usage = _extract_usage(completion)
        logger.info(
            "interview.ai.message.success stage=%s action=%s latency_ms=%s prompt_tokens=%s completion_tokens=%s total_tokens=%s",
            stage,
            action,
            int((perf_counter() - start_time) * 1000),
            usage["prompt_tokens"],
            usage["completion_tokens"],
            usage["total_tokens"],
        )
        return {
            "assistant_message": assistant_message,
            "intent": intent,
            "confidence": confidence,
        }
    except Exception:
        logger.exception(
            "interview.ai.message.failure stage=%s action=%s latency_ms=%s",
            stage,
            action,
            int((perf_counter() - start_time) * 1000),
        )
        return fallback


def evaluate_stage_rubric(
    stage: InterviewStage,
    stage_messages: list[dict[str, str]],
) -> dict[str, Any]:
    """
    Returns rubric JSON with numeric scores and summary.
    """
    start_time = perf_counter()
    fallback = _fallback_rubric(stage=stage)
    client = _build_client()
    if client is None:
        logger.info("interview.ai.rubric.fallback reason=client_unavailable stage=%s", stage)
        return fallback

    system_prompt = (
        "Evaluate interview performance for one stage only. "
        "Score each category from 0 to 2. "
        "Return strict JSON with keys: "
        "problem_understanding_score, approach_quality_score, "
        "code_correctness_reasoning_score, complexity_analysis_score, "
        "communication_clarity_score, summary."
    )

    transcript = "\n".join(
        f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in stage_messages[-10:]
    )

    try:
        completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": (
                        f"Stage: {stage}\n"
                        f"Transcript:\n{transcript}\n"
                        "Return JSON only."
                    ),
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        content = completion.choices[0].message.content or "{}"
        parsed = json.loads(content)
        normalized = _normalize_rubric(parsed)
        usage = _extract_usage(completion)
        logger.info(
            "interview.ai.rubric.success stage=%s latency_ms=%s prompt_tokens=%s completion_tokens=%s total_tokens=%s",
            stage,
            int((perf_counter() - start_time) * 1000),
            usage["prompt_tokens"],
            usage["completion_tokens"],
            usage["total_tokens"],
        )
        return normalized
    except Exception:
        logger.exception(
            "interview.ai.rubric.failure stage=%s latency_ms=%s",
            stage,
            int((perf_counter() - start_time) * 1000),
        )
        return fallback


def _build_client():
    if OpenAI is None:
        logger.error("OpenAI import failed")
        return None

    if not OPENAI_API_KEY:
        logger.error("OpenAI API Key doesn't work")
        return None

    client = OpenAI(api_key=OPENAI_API_KEY)
    return client


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
