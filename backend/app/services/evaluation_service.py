from app.core.constants import SUBMISSION_RESULT_FAIL
from app.services.python_evaluation_service import evaluate_python_submission
from app.services.javascript_evaluation_service import evaluate_javascript_submission
from app.services.java_evaluation_service import evaluate_java_submission
from app.services.cpp_evaluation_service import evaluate_cpp_submission


def evaluate_submission(code_submitted: str, language: str, test_cases: list):
    if not test_cases:
        return {
            "result": SUBMISSION_RESULT_FAIL,
            "error_message": "No test cases found for this problem",
        }

    if language == "python":
        return evaluate_python_submission(code_submitted, test_cases)
    
    if language == "javascript":
        return evaluate_javascript_submission(code_submitted, test_cases)
    
    if language == "java":
        return evaluate_java_submission(code_submitted, test_cases)
    
    if language == "cpp":
        return evaluate_cpp_submission(code_submitted, test_cases)

    return {
        "result": SUBMISSION_RESULT_FAIL,
        "error_message": f"Language '{language}' evaluation is not implemented yet",
    }
