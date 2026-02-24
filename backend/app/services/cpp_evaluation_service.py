from __future__ import annotations

import json
import subprocess
import tempfile

from app.core.constants import SUBMISSION_RESULT_FAIL, SUBMISSION_RESULT_PASS

CPP_TEST_TIMEOUT_SECONDS = 3

_CPP_RUNNER_TEMPLATE = r"""
#include <bits/stdc++.h>
using namespace std;

// User submission below
{submission_code}

static string toJsonArray(const vector<int>& arr) {{
    string out = "[";
    for (size_t i = 0; i < arr.size(); ++i) {{
        if (i > 0) out += ",";
        out += to_string(arr[i]);
    }}
    out += "]";
    return out;
}}

int main() {{
    try {{
        Solution solution;
        vector<int> nums = {{{nums_literal}}};
        int target = {target_literal};
        vector<int> output = solution.twoSum(nums, target);
        cout << "{{\"ok\":true,\"output\":" << toJsonArray(output) << "}}";
    }} catch (const exception& e) {{
        string msg = string("Exception: ") + e.what();
        for (char& c : msg) {{
            if (c == '"') c = '\'';
        }}
        cout << "{{\"ok\":false,\"error\":\"" << msg << "\"}}";
    }} catch (...) {{
        cout << "{{\"ok\":false,\"error\":\"Unknown C++ runtime error\"}}";
    }}
    return 0;
}}
"""


def evaluate_cpp_submission(code_submitted: str, test_cases: list):
    with tempfile.TemporaryDirectory(prefix="submission_eval_cpp_") as tmpdir:
        source_path = f"{tmpdir}/runner.cpp"
        binary_path = f"{tmpdir}/runner"

        for index, test_case in enumerate(test_cases, start=1):
            try:
                nums, target = _extract_two_sum_inputs(test_case.params)
            except ValueError as exc:
                return {
                    "result": SUBMISSION_RESULT_FAIL,
                    "error_message": f"Unsupported testcase shape on case #{index}: {exc}",
                }

            source = _CPP_RUNNER_TEMPLATE.format(
                submission_code=code_submitted,
                nums_literal=",".join(str(int(n)) for n in nums),
                target_literal=int(target),
            )
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
                return {
                    "result": SUBMISSION_RESULT_FAIL,
                    "error_message": f"Compilation timed out on test case #{index}",
                }
            except FileNotFoundError:
                return {
                    "result": SUBMISSION_RESULT_FAIL,
                    "error_message": "C++ runtime not available (g++ not installed)",
                }

            if compile_proc.returncode != 0:
                error_text = (compile_proc.stderr or compile_proc.stdout or "").strip()
                return {
                    "result": SUBMISSION_RESULT_FAIL,
                    "error_message": f"Compilation error on test case #{index}: {error_text[:300]}",
                }

            try:
                run_proc = subprocess.run(
                    [binary_path],
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
                runner_result = json.loads(stdout)
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
            if actual != expected:
                return {
                    "result": SUBMISSION_RESULT_FAIL,
                    "error_message": (
                        f"Wrong answer on test case #{index}. "
                        f"Expected {expected}, got {actual}"
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

