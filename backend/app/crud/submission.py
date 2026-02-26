from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models.submission import Submission
from app.db.models.user_problem import UserProblem
from app.schemas.submission import SubmissionSubmit
from app.core.constants import SUBMISSION_RESULT_FAIL, SUBMISSION_RESULT_PASS


def create_submission(submission: SubmissionSubmit, evaluation: dict, user_id: str, db: Session):
    raw_result = str(evaluation.get("result"))
    result = raw_result if raw_result in (SUBMISSION_RESULT_PASS, SUBMISSION_RESULT_FAIL) else SUBMISSION_RESULT_FAIL

    db_submission = Submission(
        code_submitted=submission.code_submitted,
        result=result,
        language=submission.language,
        user_id=user_id,
        problem_id=submission.problem_id,
        error=evaluation.get("error_message")
    )
    db.add(db_submission)
    db.flush()

    submission_time = db_submission.created_at or datetime.utcnow()
    _upsert_user_problem_progress(
        db=db,
        user_id=user_id,
        problem_id=submission.problem_id,
        submission_id=db_submission.id,
        submission_time=submission_time,
        did_pass=result == SUBMISSION_RESULT_PASS,
    )

    db.commit()
    db.refresh(db_submission)
    return db_submission


def get_submissions(
    db: Session,
    user_id: str | None = None,
    problem_id: str | None = None,
    language: str | None = None,
):
    query = db.query(Submission)
    if user_id is not None:
        query = query.filter(Submission.user_id == user_id)
    if problem_id is not None:
        query = query.filter(Submission.problem_id == problem_id)
    if language is not None:
        query = query.filter(Submission.language == language)
    return query.order_by(Submission.created_at.desc()).all()


def _upsert_user_problem_progress(
    db: Session,
    user_id: str,
    problem_id: str,
    submission_id: str | None,
    submission_time: datetime,
    did_pass: bool,
):
    row = (
        db.query(UserProblem)
        .filter(UserProblem.user_id == user_id, UserProblem.problem_id == problem_id)
        .first()
    )

    if row is None:
        row = UserProblem(
            user_id=user_id,
            problem_id=problem_id,
            is_passed=did_pass,
            first_passed_at=submission_time if did_pass else None,
            last_submission_at=submission_time,
            last_submission_id=submission_id,
        )
        db.add(row)
        return

    row.last_submission_at = submission_time
    row.last_submission_id = submission_id
    if did_pass:
        row.is_passed = True
        if row.first_passed_at is None:
            row.first_passed_at = submission_time
