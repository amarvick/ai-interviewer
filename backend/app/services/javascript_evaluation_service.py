from __future__ import annotations

import json
import subprocess
import tempfile
from typing import Any

from app.core.constants import SUBMISSION_RESULT_FAIL, SUBMISSION_RESULT_PASS

JS_TEST_TIMEOUT_SECONDS = 2

_JS_RUNNER_SCRIPT = r"""
const fs = require("fs");
const path = require("path");

function loadSubmission(submissionPath) {
  const resolvedPath = path.resolve(submissionPath);
  delete require.cache[resolvedPath];
  return require(resolvedPath);
}

function pickCallable(submissionModule) {
  if (typeof submissionModule === "function") {
    return submissionModule;
  }

  if (submissionModule && typeof submissionModule.solve === "function") {
    return submissionModule.solve.bind(submissionModule);
  }

  const maybeDefault = submissionModule && submissionModule.default ? submissionModule.default : null;
  if (maybeDefault && typeof maybeDefault === "function") {
    return maybeDefault;
  }
  if (maybeDefault && typeof maybeDefault.solve === "function") {
    return maybeDefault.solve.bind(maybeDefault);
  }

  const Solution =
    (submissionModule && submissionModule.Solution) ||
    (maybeDefault && maybeDefault.Solution);

  if (typeof Solution === "function") {
    const instance = new Solution();
    const preferred = ["solve", "twoSum"];
    for (const methodName of preferred) {
      if (typeof instance[methodName] === "function") {
        return instance[methodName].bind(instance);
      }
    }

    for (const key of Object.keys(instance)) {
      if (typeof instance[key] === "function") {
        return instance[key].bind(instance);
      }
    }
  }

  throw new Error(
    "No callable entrypoint found. Export `solve(...)` or class `Solution` with a public method."
  );
}

function unpackParams(params) {
  if (Array.isArray(params)) {
    return params;
  }

  if (
    params &&
    typeof params === "object" &&
    (Object.prototype.hasOwnProperty.call(params, "args") ||
      Object.prototype.hasOwnProperty.call(params, "kwargs"))
  ) {
    const args = Array.isArray(params.args) ? params.args : [];
    const kwargs = params.kwargs && typeof params.kwargs === "object" ? params.kwargs : {};
    return [...args, ...Object.keys(kwargs).map((key) => kwargs[key])];
  }

  if (params && typeof params === "object") {
    return Object.keys(params).map((key) => params[key]);
  }

  return [params];
}

async function main() {
  const submissionPath = process.argv[2];
  const testcasePath = process.argv[3];

  try {
    const payload = JSON.parse(fs.readFileSync(testcasePath, "utf-8"));
    const params = payload.params;

    const submissionModule = loadSubmission(submissionPath);
    const callable = pickCallable(submissionModule);
    const args = unpackParams(params);
    const output = await Promise.resolve(callable(...args));

    console.log(JSON.stringify({ ok: true, output }));
  } catch (error) {
    console.log(
      JSON.stringify({
        ok: false,
        error: `${error && error.name ? error.name : "Error"}: ${
          error && error.message ? error.message : String(error)
        }`,
      })
    );
  }
}

if (require.main === module) {
  main();
}
"""


def evaluate_javascript_submission(code_submitted: str, test_cases: list):
    with tempfile.TemporaryDirectory(prefix="submission_eval_js_") as tmpdir:
        submission_path = f"{tmpdir}/submission.js"
        runner_path = f"{tmpdir}/runner.js"

        with open(submission_path, "w", encoding="utf-8") as f:
            f.write(code_submitted)
        with open(runner_path, "w", encoding="utf-8") as f:
            f.write(_JS_RUNNER_SCRIPT)

        for index, test_case in enumerate(test_cases, start=1):
            case_payload = {"params": test_case.params}
            case_path = f"{tmpdir}/testcase_{index}.json"
            with open(case_path, "w", encoding="utf-8") as f:
                json.dump(case_payload, f)

            try:
                completed = subprocess.run(
                    ["node", runner_path, submission_path, case_path],
                    capture_output=True,
                    text=True,
                    timeout=JS_TEST_TIMEOUT_SECONDS,
                    check=False,
                )
            except subprocess.TimeoutExpired:
                return {
                    "result": SUBMISSION_RESULT_FAIL,
                    "error_message": f"Time limit exceeded on test case #{index}",
                }
            except FileNotFoundError:
                return {
                    "result": SUBMISSION_RESULT_FAIL,
                    "error_message": "JavaScript runtime not available (node is not installed)",
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
