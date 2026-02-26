from __future__ import annotations

import json
import subprocess
import tempfile
from typing import Any

from app.core.constants import SUBMISSION_RESULT_FAIL, SUBMISSION_RESULT_PASS

JAVA_TEST_TIMEOUT_SECONDS = 3

_JAVA_RUNNER_SOURCE = r"""
import java.lang.reflect.*;

public class Runner {
    public static void main(String[] args) {
        try {
            int[] nums = parseNums(args.length > 0 ? args[0] : "");
            int target = Integer.parseInt(args.length > 1 ? args[1] : "0");

            Solution solution = new Solution();
            Method method = pickMethod(solution.getClass());
            Object result = method.invoke(solution, nums, target);

            System.out.println("{\"ok\":true,\"output\":" + toJson(result) + "}");
        } catch (Throwable t) {
            Throwable cause = t instanceof InvocationTargetException && t.getCause() != null ? t.getCause() : t;
            String msg = cause.getClass().getSimpleName() + ": " + String.valueOf(cause.getMessage());
            msg = msg.replace("\\", "\\\\").replace("\"", "\\\"");
            System.out.println("{\"ok\":false,\"error\":\"" + msg + "\"}");
        }
    }

    private static Method pickMethod(Class<?> cls) throws NoSuchMethodException {
        String[] preferred = new String[] { "solve", "twoSum" };
        for (String name : preferred) {
            try {
                return cls.getMethod(name, int[].class, int.class);
            } catch (NoSuchMethodException ignored) {}
        }
        for (Method m : cls.getMethods()) {
            if (m.getParameterCount() == 2) {
                Class<?>[] p = m.getParameterTypes();
                if (p[0] == int[].class && (p[1] == int.class || p[1] == Integer.class)) {
                    return m;
                }
            }
        }
        throw new NoSuchMethodException("No compatible method found (expected solve/twoSum(int[], int))");
    }

    private static int[] parseNums(String csv) {
        if (csv == null || csv.isEmpty()) return new int[0];
        String[] parts = csv.split(",");
        int[] nums = new int[parts.length];
        for (int i = 0; i < parts.length; i++) nums[i] = Integer.parseInt(parts[i]);
        return nums;
    }

    private static String toJson(Object obj) {
        if (obj == null) return "null";
        if (obj instanceof int[]) {
            int[] arr = (int[]) obj;
            StringBuilder sb = new StringBuilder("[");
            for (int i = 0; i < arr.length; i++) {
                if (i > 0) sb.append(",");
                sb.append(arr[i]);
            }
            sb.append("]");
            return sb.toString();
        }
        if (obj instanceof java.util.List) {
            java.util.List<?> list = (java.util.List<?>) obj;
            StringBuilder sb = new StringBuilder("[");
            for (int i = 0; i < list.size(); i++) {
                if (i > 0) sb.append(",");
                sb.append(String.valueOf(list.get(i)));
            }
            sb.append("]");
            return sb.toString();
        }
        return String.valueOf(obj);
    }
}
"""


def evaluate_java_submission(code_submitted: str, test_cases: list):
    with tempfile.TemporaryDirectory(prefix="submission_eval_java_") as tmpdir:
        submission_path = f"{tmpdir}/Solution.java"
        runner_path = f"{tmpdir}/Runner.java"

        with open(submission_path, "w", encoding="utf-8") as f:
            f.write(code_submitted)
        with open(runner_path, "w", encoding="utf-8") as f:
            f.write(_JAVA_RUNNER_SOURCE)

        try:
            compile_proc = subprocess.run(
                ["javac", submission_path, runner_path],
                capture_output=True,
                text=True,
                timeout=JAVA_TEST_TIMEOUT_SECONDS,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return {"result": SUBMISSION_RESULT_FAIL, "error_message": "Compilation timed out"}
        except FileNotFoundError:
            return {
                "result": SUBMISSION_RESULT_FAIL,
                "error_message": "Java runtime not available (javac/java not installed)",
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
                    ["java", "-cp", tmpdir, "Runner", _to_csv(nums), str(int(target))],
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

