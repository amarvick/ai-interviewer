# Interview Tables Migration

Adds the three interview tables:

- `interview_sessions`
- `interview_messages`
- `interview_evaluations`

## Design notes

- `interview_messages` does **not** include `problem_id` because that is already available through:
  - `interview_messages.session_id -> interview_sessions.problem_id`
- `interview_evaluations` includes both category scores and optional `rubric_json` for future rubric expansion.

## Apply

From repo root:

```bash
docker exec -i ai_interviewer_db psql -U postgres -d ai_interviewer < backend/docs/interview_tables_migration.sql
```

## Verify

```bash
docker exec -it ai_interviewer_db psql -U postgres -d ai_interviewer
```

Then:

```sql
\d interview_sessions
\d interview_messages
\d interview_evaluations
```
