from __future__ import annotations

import json
import subprocess
import tempfile

from app.core.constants import SUBMISSION_RESULT_FAIL, SUBMISSION_RESULT_PASS

JAVA_TEST_TIMEOUT_SECONDS = 3

_JAVA_RUNNER_TEMPLATE = """
import java.util.Arrays;

public class Runner {{
    public static void main(String[] args) {{
        try {{
            Solution solution = new Solution();
            int[] nums = new int[]{{{nums_literal}}};
            int target = {target_literal};
            int[] output = solution.twoSum(nums, target);
            System.out.println("{{\\"ok\\":true,\\"output\\":" + toJsonArray(output) + "}}");
        }} catch (Throwable t) {{
            String msg = t.getClass().getSimpleName() + ": " + (t.getMessage() == null ? "" : t.getMessage());
            msg = msg.replace("\\\\", "\\\\\\\\").replace("\\"", "\\\\\\"");
            System.out.println("{{\\"ok\\":false,\\"error\\":\\"" + msg + "\\"}}");
        }}
    }}

    private static String toJsonArray(int[] arr) {{
        if (arr == null) {{
            return "null";
        }}
        StringBuilder sb = new StringBuilder();
        sb.append("[");
        for (int i = 0; i < arr.length; i++) {{
            if (i > 0) sb.append(",");
            sb.append(arr[i]);
        }}
        sb.append("]");
        return sb.toString();
    }}
}}
"""


def evaluate_java_submission(code_submitted: str, test_cases: list):
    with tempfile.TemporaryDirectory(prefix="submission_eval_java_") as tmpdir:
        submission_path = f"{tmpdir}/Submission.java"
        runner_path = f"{tmpdir}/Runner.java"

        with open(submission_path, "w", encoding="utf-8") as f:
            f.write(code_submitted)

        for index, test_case in enumerate(test_cases, start=1):
            try:
                nums, target = _extract_two_sum_inputs(test_case.params)
            except ValueError as exc:
                return {
                    "result": SUBMISSION_RESULT_FAIL,
                    "error_message": f"Unsupported testcase shape on case #{index}: {exc}",
                }

            runner_source = _JAVA_RUNNER_TEMPLATE.format(
                nums_literal=",".join(str(int(n)) for n in nums),
                target_literal=int(target),
            )
            with open(runner_path, "w", encoding="utf-8") as f:
                f.write(runner_source)

            try:
                compile_proc = subprocess.run(
                    ["javac", submission_path, runner_path],
                    capture_output=True,
                    text=True,
                    timeout=JAVA_TEST_TIMEOUT_SECONDS,
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
                    "error_message": "Java runtime not available (javac/java not installed)",
                }

            if compile_proc.returncode != 0:
                error_text = (compile_proc.stderr or compile_proc.stdout or "").strip()
                return {
                    "result": SUBMISSION_RESULT_FAIL,
                    "error_message": f"Compilation error on test case #{index}: {error_text[:300]}",
                }

            try:
                run_proc = subprocess.run(
                    ["java", "-cp", tmpdir, "Runner"],
                    capture_output=True,
                    text=True,
                    timeout=JAVA_TEST_TIMEOUT_SECONDS,
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

