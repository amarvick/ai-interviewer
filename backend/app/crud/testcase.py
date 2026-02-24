from sqlalchemy.orm import Session
from app.db.models.testcase import TestCase


def get_testcases_by_problem_id(db: Session, problem_id: str):
    return db.query(TestCase).filter(TestCase.problem_id == problem_id).all()


def get_public_testcases_by_problem_id(db: Session, problem_id: str):
    return (
        db.query(TestCase)
        .filter(TestCase.problem_id == problem_id, TestCase.is_hidden.is_(False))
        .all()
    )
