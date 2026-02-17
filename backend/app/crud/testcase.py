from sqlalchemy.orm import Session
from app.db.models.testcase import TestCase
from app.schemas.testcase import TestCaseCreate

def create_testcase(testcase: TestCaseCreate, db: Session):
    db_testcase = TestCase(
        problem_id=testcase.problem_id,
        params=testcase.params,
        expected_output=testcase.expected_output,
        is_hidden=testcase.is_hidden
    )
    db.add(db_testcase)
    db.commit()
    db.refresh(db_testcase)
    return db_testcase

def get_testcases_by_problem_id(db: Session, problem_id: int):
    return db.query(TestCase).filter(TestCase.problem_id == problem_id).all()
