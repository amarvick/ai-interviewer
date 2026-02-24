# Submission Table Migration

You renamed backend code from `Attempt` to `Submission`.  
Because this project currently uses `Base.metadata.create_all()` (not Alembic), table renames are **not** automatic.
Also, adding `Submission.language` requires an explicit DB migration because `create_all()` does not alter existing tables.

## Option 1: No existing submission data (recommended for your current state)

1. Open psql:
```bash
docker exec -it ai_interviewer_db psql -U postgres -d ai_interviewer
```
2. Run:
```sql
DROP TABLE IF EXISTS attempts CASCADE;
```
3. Start backend once:
```bash
cd backend
uvicorn app.main:app --reload
```
4. Verify table exists:
```sql
\dt
\d submissions
SELECT id, user_id, problem_id, language, result, created_at FROM submissions LIMIT 5;
```

## Option 2: Keep existing data (safe rename path)

1. Run the SQL script:
```bash
docker exec -it ai_interviewer_db psql -U postgres -d ai_interviewer -f /Users/alexmarvick/Desktop/Personal/Programming/ai-interviewer/backend/docs/submission_migration.sql
```
2. Verify:
```sql
\dt
\d submissions
```

## Relationship notes

- `submissions.user_id -> users.id` and `submissions.problem_id -> problems.id` remain valid after rename.
- `submissions.language` is now required and indexed.
- App-side ORM relationships are already updated to:
  - `User.submissions`
  - `Problem.submissions`

## Recommended next step (future-proofing)

Add Alembic so future schema changes are explicit and versioned:

1. `pip install alembic`
2. `alembic init alembic`
3. Configure `sqlalchemy.url` and metadata target.
4. Create migrations for future table/column renames instead of relying on `create_all()`.
