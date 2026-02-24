from fastapi import HTTPException
from app.schemas.submission import SubmissionSubmit
from app.crud.problem import get_problem_by_id
from app.crud.testcase import get_testcases_by_problem_id
from app.services import evaluation_service


def submit_solution(submission: SubmissionSubmit, db):
    problem = get_problem_by_id(db, submission.problem_id)
    if problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")

    supported_languages = set((problem.starter_code or {}).keys())
    if submission.language not in supported_languages:
        raise HTTPException(
            status_code=400,
            detail=f"Language '{submission.language}' is not supported for this problem",
        )

    db_test_cases = get_testcases_by_problem_id(db, submission.problem_id)
    print("******************************* EVALUATING SUBMISSION *******************************")
    print(submission.code_submitted)
    result = evaluation_service.evaluate_submission(
        code_submitted=submission.code_submitted,
        language=submission.language,
        test_cases=db_test_cases,
    )
    return result
