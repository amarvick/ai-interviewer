from typing import Final, Literal

SUBMISSION_RESULT_PASS: Final[str] = "pass"
SUBMISSION_RESULT_FAIL: Final[str] = "fail"

SubmissionResult = Literal["pass", "fail"]
Language = Literal["python", "javascript", "java", "cpp"]

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

InterviewAction = Literal["ask_question", "nudge", "advance", "stay"]
