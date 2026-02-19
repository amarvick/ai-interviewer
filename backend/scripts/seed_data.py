"""
Seed script for initial ProblemList rows.

Run from backend/:
    source venv/bin/activate
    python scripts/seed_data.py
"""

from pathlib import Path
import sys

# Ensure "app" package is importable when running as a script path.
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.db.database import Base, SessionLocal, engine
from app.db.models import ProblemList
import app.db.models  # noqa: F401  # ensure all models are registered before create_all


PROBLEM_LISTS = [
    ("blind_75", "Blind 75", "https://dummyimage.com/96x96/1f2a5e/cfe2ff&text=B75"),
    ("taro_75", "Taro 75", "https://dummyimage.com/96x96/1f2a5e/cfe2ff&text=T75"),
    ("neetcode_150", "Neetcode 150", "https://dummyimage.com/96x96/1f2a5e/cfe2ff&text=N150"),
    ("google_50", "Google 50", "https://dummyimage.com/96x96/1f2a5e/cfe2ff&text=G50"),
    ("meta_50", "Meta 50", "https://dummyimage.com/96x96/1f2a5e/cfe2ff&text=M50"),
    ("amazon_50", "Amazon 50", "https://dummyimage.com/96x96/1f2a5e/cfe2ff&text=A50"),
    ("microsoft_30", "Microsoft 30", "https://dummyimage.com/96x96/1f2a5e/cfe2ff&text=MS30"),
    ("apple_30", "Apple 30", "https://dummyimage.com/96x96/1f2a5e/cfe2ff&text=AP30"),
]


def seed_problem_lists() -> None:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        inserted = 0
        updated = 0
        skipped = 0

        for seed_id, name, icon_url in PROBLEM_LISTS:
            existing = db.query(ProblemList).filter(ProblemList.id == seed_id).first()
            if existing:
                changed = False
                if existing.name != name:
                    existing.name = name
                    changed = True
                if existing.icon_url != icon_url:
                    existing.icon_url = icon_url
                    changed = True

                if changed:
                    updated += 1
                else:
                    skipped += 1
                continue

            existing_by_name = db.query(ProblemList).filter(ProblemList.name == name).first()
            if existing_by_name:
                changed = False
                if existing_by_name.id != seed_id:
                    existing_by_name.id = seed_id
                    changed = True
                if existing_by_name.icon_url != icon_url:
                    existing_by_name.icon_url = icon_url
                    changed = True

                if changed:
                    updated += 1
                else:
                    skipped += 1
                continue

            db.add(ProblemList(id=seed_id, name=name, icon_url=icon_url))
            inserted += 1

        db.commit()
        print(f"Seeding complete. Inserted: {inserted}, Updated: {updated}, Skipped: {skipped}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_problem_lists()
