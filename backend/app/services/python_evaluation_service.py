from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from typing import Any

from app.core.constants import SUBMISSION_RESULT_FAIL, SUBMISSION_RESULT_PASS

PYTHON_TEST_TIMEOUT_SECONDS = 2

_PYTHON_RUNNER_SCRIPT = r"""
import importlib.util
import json
import sys
import traceback
import typing as _typing


def _load_module(path: str):
    spec = importlib.util.spec_from_file_location("submission_module", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load submission module")
    module = importlib.util.module_from_spec(spec)
    # Common typing aliases so user code using List/Dict/etc annotations works
    # even when they omit `from typing import ...`.
    module.List = _typing.List
    module.Dict = _typing.Dict
    module.Tuple = _typing.Tuple
    module.Set = _typing.Set
    module.Optional = _typing.Optional
    module.Any = _typing.Any
    spec.loader.exec_module(module)
    return module


def _pick_callable(module):
    if hasattr(module, "solve") and callable(getattr(module, "solve")):
        return getattr(module, "solve")

    if hasattr(module, "Solution"):
        instance = module.Solution()
        preferred = ("solve", "twoSum")
        for method_name in preferred:
            if hasattr(instance, method_name) and callable(getattr(instance, method_name)):
                return getattr(instance, method_name)

        # Last-resort: first non-dunder callable on Solution instance.
        for name in dir(instance):
            if name.startswith("_"):
                continue
            candidate = getattr(instance, name)
            if callable(candidate):
                return candidate

    raise RuntimeError(
        "No callable entrypoint found. Define `solve(...)` or class `Solution` with a public method."
    )


def _unpack_params(params):
    # Preferred explicit shape.
    if isinstance(params, dict) and ("args" in params or "kwargs" in params):
        args = params.get("args", [])
        kwargs = params.get("kwargs", {})
        return args, kwargs

    # Common problem shape like {"nums": [...], "target": 7}
    if isinstance(params, dict):
        return [], params

    # Positional inputs.
    if isinstance(params, list):
        return params, {}

    return [params], {}


def main():
    submission_path = sys.argv[1]
    testcase_path = sys.argv[2]

    try:
        with open(testcase_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        params = payload.get("params")

        module = _load_module(submission_path)
        target_callable = _pick_callable(module)
        args, kwargs = _unpack_params(params)
        output = target_callable(*args, **kwargs)

        print(json.dumps({"ok": True, "output": output}, default=str))
    except Exception as exc:
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": f"{type(exc).__name__}: {exc}",
                    "traceback": traceback.format_exc(),
                }
            )
        )


if __name__ == "__main__":
    main()
"""


def evaluate_python_submission(code_submitted: str, test_cases: list):
    with tempfile.TemporaryDirectory(prefix="submission_eval_") as tmpdir:
        submission_path = f"{tmpdir}/submission.py"
        runner_path = f"{tmpdir}/runner.py"

        with open(submission_path, "w", encoding="utf-8") as f:
            f.write(code_submitted)
        with open(runner_path, "w", encoding="utf-8") as f:
            f.write(_PYTHON_RUNNER_SCRIPT)

        for index, test_case in enumerate(test_cases, start=1):
            case_payload = {"params": test_case.params}
            case_path = f"{tmpdir}/testcase_{index}.json"
            with open(case_path, "w", encoding="utf-8") as f:
                json.dump(case_payload, f)

            try:
                completed = subprocess.run(
                    [sys.executable, runner_path, submission_path, case_path],
                    capture_output=True,
                    text=True,
                    timeout=PYTHON_TEST_TIMEOUT_SECONDS,
                    check=False,
                )
            except subprocess.TimeoutExpired:
                return {
                    "result": SUBMISSION_RESULT_FAIL,
                    "error_message": f"Time limit exceeded on test case #{index}",
                }

            stdout = completed.stdout.strip()
            if not stdout:
                return {
                    "result": SUBMISSION_RESULT_FAIL,
                    "error_message": f"Empty runner output on test case #{index}",
                }

            try:
                runner_result = _parse_runner_output(stdout)
            except json.JSONDecodeError:
                return {
                    "result": SUBMISSION_RESULT_FAIL,
                    "error_message": (
                        f"Invalid runner output on test case #{index}: {stdout[:200]}"
                    ),
                }

            if not runner_result.get("ok"):
                return {
                    "result": SUBMISSION_RESULT_FAIL,
                    "error_message": (
                        f"Runtime error on test case #{index}: "
                        f"{runner_result.get('error', 'unknown error')}"
                    ),
                }

            actual = runner_result.get("output")
            expected = test_case.expected_output
            if not _outputs_match(actual, expected):
                return {
                    "result": SUBMISSION_RESULT_FAIL,
                    "error_message": (
                        f"Wrong answer on test case #{index}. "
                        f"Expected {expected}, got {actual}"
                    ),
                }

    return {"result": SUBMISSION_RESULT_PASS, "error_message": None}


def _outputs_match(actual: Any, expected: Any) -> bool:
    if actual == expected:
        return True
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        return abs(float(actual) - float(expected)) < 1e-9
    return False


def _parse_runner_output(stdout: str) -> dict[str, Any]:
    lines = [line for line in stdout.splitlines() if line.strip()]
    if not lines:
        raise json.JSONDecodeError("empty output", "", 0)
    return json.loads(lines[-1])
