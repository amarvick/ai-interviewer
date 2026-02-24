from app.schemas.submission import SubmissionSubmit
from app.crud.testcase import get_testcases_by_problem_id
from app.services import evaluation_service

def submit_solution(submission: SubmissionSubmit, db):
    db_test_cases = get_testcases_by_problem_id(db, submission.problem_id)
    result = evaluation_service.evaluate_submission(submission.code_submitted, db_test_cases)
    return result
    
