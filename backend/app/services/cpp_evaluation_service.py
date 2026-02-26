from __future__ import annotations

import json
import subprocess
import tempfile
from typing import Any

from app.core.constants import SUBMISSION_RESULT_FAIL, SUBMISSION_RESULT_PASS

CPP_TEST_TIMEOUT_SECONDS = 3

_CPP_RUNNER_TEMPLATE = r"""
#include <bits/stdc++.h>
using namespace std;

__SUBMISSION_CODE__

static vector<int> parseNums(const string& csv) {
    vector<int> out;
    if (csv.empty()) return out;
    string token;
    stringstream ss(csv);
    while (getline(ss, token, ',')) {
        if (!token.empty()) out.push_back(stoi(token));
    }
    return out;
}

static string toJsonArray(const vector<int>& arr) {
    string out = "[";
    for (size_t i = 0; i < arr.size(); ++i) {
        if (i > 0) out += ",";
        out += to_string(arr[i]);
    }
    out += "]";
    return out;
}

int main(int argc, char** argv) {
    try {
        string numsCsv = argc > 1 ? argv[1] : "";
        int target = argc > 2 ? stoi(argv[2]) : 0;
        vector<int> nums = parseNums(numsCsv);

        Solution solution;
        vector<int> output = solution.twoSum(nums, target);
        cout << "{\"ok\":true,\"output\":" << toJsonArray(output) << "}";
    } catch (const exception& e) {
        string msg = string("Exception: ") + e.what();
        for (char& c : msg) {
            if (c == '"') c = '\'';
        }
        cout << "{\"ok\":false,\"error\":\"" << msg << "\"}";
    } catch (...) {
        cout << "{\"ok\":false,\"error\":\"Unknown C++ runtime error\"}";
    }
    return 0;
}
"""


def evaluate_cpp_submission(code_submitted: str, test_cases: list):
    with tempfile.TemporaryDirectory(prefix="submission_eval_cpp_") as tmpdir:
        source_path = f"{tmpdir}/runner.cpp"
        binary_path = f"{tmpdir}/runner"

        source = _CPP_RUNNER_TEMPLATE.replace("__SUBMISSION_CODE__", code_submitted)
        with open(source_path, "w", encoding="utf-8") as f:
            f.write(source)

        try:
            compile_proc = subprocess.run(
                ["g++", "-std=c++17", source_path, "-O2", "-o", binary_path],
                capture_output=True,
                text=True,
                timeout=CPP_TEST_TIMEOUT_SECONDS,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return {"result": SUBMISSION_RESULT_FAIL, "error_message": "Compilation timed out"}
        except FileNotFoundError:
            return {
                "result": SUBMISSION_RESULT_FAIL,
                "error_message": "C++ runtime not available (g++ not installed)",
            }

        if compile_proc.returncode != 0:
            error_text = (compile_proc.stderr or compile_proc.stdout or "").strip()
            return {"result": SUBMISSION_RESULT_FAIL, "error_message": f"Compilation error: {error_text[:300]}"}

        for index, test_case in enumerate(test_cases, start=1):
            try:
                nums, target = _extract_two_sum_inputs(test_case.params)
            except ValueError as exc:
                return {
                    "result": SUBMISSION_RESULT_FAIL,
                    "error_message": f"Unsupported testcase shape on case #{index}: {exc}",
                }

            try:
                run_proc = subprocess.run(
                    [binary_path, _to_csv(nums), str(int(target))],
                    capture_output=True,
                    text=True,
                    timeout=CPP_TEST_TIMEOUT_SECONDS,
                    check=False,
                )
            except subprocess.TimeoutExpired:
                return {
                    "result": SUBMISSION_RESULT_FAIL,
                    "error_message": f"Time limit exceeded on test case #{index}",
                }

            stdout = run_proc.stdout.strip()
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
                    "error_message": f"Invalid runner output on test case #{index}: {stdout[:200]}",
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
                        f"Wrong answer on test case #{index}. Expected {expected}, got {actual}"
                    ),
                }

    return {"result": SUBMISSION_RESULT_PASS, "error_message": None}


def _extract_two_sum_inputs(params):
    if isinstance(params, dict):
        if "nums" in params and "target" in params:
            return params["nums"], params["target"]
        if "args" in params and isinstance(params["args"], list) and len(params["args"]) >= 2:
            return params["args"][0], params["args"][1]
    if isinstance(params, list) and len(params) >= 2:
        return params[0], params[1]
    raise ValueError("expected params to include nums/target or args[0]/args[1]")


def _to_csv(values: list[Any]) -> str:
    return ",".join(str(int(v)) for v in values)


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

