from app.schemas.attempt import AttemptSubmit
from app.crud.testcase import get_testcases_by_problem_id
from app.services import evaluation_service

def submit_solution(attempt: AttemptSubmit, db):
    db_test_cases = get_testcases_by_problem_id(db, attempt.problem_id)
    result = evaluation_service.evaluate_attempt(attempt.code_submitted, db_test_cases) 
    return result
    