from typing import Final, Literal

ATTEMPT_RESULT_PASS: Final[str] = "pass"
ATTEMPT_RESULT_FAIL: Final[str] = "fail"

AttemptResult = Literal["pass", "fail"]
