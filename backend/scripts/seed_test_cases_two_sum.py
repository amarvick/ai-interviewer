"""
Seed script for test cases for the "Two Sum" problem.

Run from backend/:
    source venv/bin/activate
    python scripts/seed_test_cases_two_sum.py
"""

from pathlib import Path
import json
import sys

# Ensure "app" package is importable when running as a script path.
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.db.database import Base, SessionLocal, engine
from app.db.models import Problem, TestCase
import app.db.models  # noqa: F401  # ensure all models are registered before create_all


TARGET_PROBLEM_ID = "1"
TARGET_PROBLEM_TITLE = "Two Sum"

TWO_SUM_TEST_CASES = [
    {
        "params": {"nums": [2, 7, 11, 15], "target": 9},
        "expected_output": [0, 1],
        "is_hidden": False,
    },
    {
        "params": {"nums": [1, 4, 10, -3], "target": 14},
        "expected_output": [1, 2],
        "is_hidden": False,
    },
    {
        "params": {"nums": [3, 2, 4], "target": 6},
        "expected_output": [1, 2],
        "is_hidden": False,
    },
    {
        "params": {"nums": [0, 4, 3, 0], "target": 0},
        "expected_output": [0, 3],
        "is_hidden": False,
    },
    {
        "params": {"nums": [1, -2, 5, 10], "target": -1},
        "expected_output": [0, 1],
        "is_hidden": False,
    },
    {
        "params": {"nums": [-1, -2, -3, -4, -5], "target": -8},
        "expected_output": [2, 4],
        "is_hidden": False,
    },
]


def _params_key(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def seed_two_sum_test_cases() -> None:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        problem = db.query(Problem).filter(Problem.id == TARGET_PROBLEM_ID).first()
        if problem is None:
            problem = db.query(Problem).filter(Problem.title == TARGET_PROBLEM_TITLE).first()

        if problem is None:
            raise RuntimeError(
                "Two Sum problem not found. Seed the problem first via scripts/seed_problem_two_sum.py"
            )

        print(f"Seeding test cases for problem id={problem.id!r}, title={problem.title!r}")

        existing = db.query(TestCase).filter(TestCase.problem_id == problem.id).all()
        existing_by_params = {_params_key(tc.params): tc for tc in existing}
        seed_params_keys = {_params_key(tc["params"]) for tc in TWO_SUM_TEST_CASES}

        inserted = 0
        updated = 0
        skipped = 0
        deleted = 0

        for seed_case in TWO_SUM_TEST_CASES:
            key = _params_key(seed_case["params"])
            current = existing_by_params.get(key)
            if current is None:
                db.add(
                    TestCase(
                        problem_id=problem.id,
                        params=seed_case["params"],
                        expected_output=seed_case["expected_output"],
                        is_hidden=seed_case["is_hidden"],
                    )
                )
                inserted += 1
                continue

            changed = False
            if current.expected_output != seed_case["expected_output"]:
                current.expected_output = seed_case["expected_output"]
                changed = True
            if bool(current.is_hidden) != bool(seed_case["is_hidden"]):
                current.is_hidden = seed_case["is_hidden"]
                changed = True

            if changed:
                updated += 1
            else:
                skipped += 1

        # Remove stale test cases for this problem that are not in this seed set.
        for current in existing:
            key = _params_key(current.params)
            if key not in seed_params_keys:
                db.delete(current)
                deleted += 1

        db.commit()
        print(
            f"Done. Inserted: {inserted}, Updated: {updated}, "
            f"Skipped: {skipped}, Deleted stale: {deleted}"
        )
    finally:
        db.close()


if __name__ == "__main__":
    seed_two_sum_test_cases()
