from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field


InterviewStage = Literal[
    "INTRO",
    "CLARIFICATION",
    "APPROACH_DISCUSSION",
    "PSEUDOCODE",
    "CODING",
    "COMPLEXITY_DISCUSSION",
    "FOLLOW_UP",
    "FEEDBACK",
    "COMPLETE",
]

InterviewSessionStatus = Literal["ACTIVE", "COMPLETED", "ABANDONED"]
InterviewMessageRole = Literal["system", "assistant", "user"]


class InterviewSessionCreate(BaseModel):
    problem_id: str


class InterviewSessionUpdateStage(BaseModel):
    stage: InterviewStage


class InterviewSessionComplete(BaseModel):
    final_score: float | None = Field(default=None, ge=0, le=50)


class InterviewMessageCreate(BaseModel):
    content: str
    role: InterviewMessageRole = "user"
    has_submission: bool = False
    current_code: str | None = None
    chat_history: list[dict[str, str]] = Field(default_factory=list)


class InterviewEvaluationCreate(BaseModel):
    stage: InterviewStage
    problem_understanding_score: int = Field(ge=0, le=10)
    approach_quality_score: int = Field(ge=0, le=10)
    code_correctness_reasoning_score: int = Field(ge=0, le=10)
    complexity_analysis_score: int = Field(ge=0, le=10)
    communication_clarity_score: int = Field(ge=0, le=10)
    total_score: float = Field(ge=0, le=50)
    passed: bool = False
    summary: str | None = None
    rubric_json: dict[str, Any] = Field(default_factory=dict)


class InterviewMessageResponse(BaseModel):
    id: str
    session_id: str
    user_id: str | None = None
    role: InterviewMessageRole
    content: str
    stage_at_message: InterviewStage
    created_at: datetime

    class Config:
        orm_mode = True


class InterviewEvaluationResponse(BaseModel):
    id: str
    session_id: str
    stage: InterviewStage
    problem_understanding_score: int
    approach_quality_score: int
    code_correctness_reasoning_score: int
    complexity_analysis_score: int
    communication_clarity_score: int
    total_score: float
    passed: bool
    summary: str | None = None
    rubric_json: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    class Config:
        orm_mode = True


class InterviewSessionResponse(BaseModel):
    id: str
    user_id: str
    problem_id: str
    stage: InterviewStage
    status: InterviewSessionStatus
    final_score: float | None = None
    stuck_signal_count: int = 0
    nudges_used_in_stage: int = 0
    started_at: datetime
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class InterviewSessionDetailResponse(InterviewSessionResponse):
    messages: list[InterviewMessageResponse] = Field(default_factory=list)
    evaluations: list[InterviewEvaluationResponse] = Field(default_factory=list)
    can_code: bool = False


class InterviewCompletionResponse(InterviewSessionResponse):
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
