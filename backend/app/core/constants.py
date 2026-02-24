from typing import Final, Literal

SUBMISSION_RESULT_PASS: Final[str] = "pass"
SUBMISSION_RESULT_FAIL: Final[str] = "fail"

SubmissionResult = Literal["pass", "fail"]
Language = Literal["python", "javascript", "java", "cpp"]
