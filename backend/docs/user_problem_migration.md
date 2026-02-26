# User Problem Progress Migration

Adds `user_problems` to track completion/progress per `(user_id, problem_id)`.

## Table shape

- `user_id` FK -> `users.id`
- `problem_id` FK -> `problems.id`
- `is_passed` boolean
- `first_passed_at` nullable datetime
- `last_submission_at` datetime
- `last_submission_id` nullable FK -> `submissions.id`
- all IDs/FKs are string IDs (`varchar(64)`)
- unique `(user_id, problem_id)`

## Apply

From repo root:

```bash
docker exec -i ai_interviewer_db psql -U postgres -d ai_interviewer < backend/docs/user_problem_migration.sql
```

## Verify

```bash
docker exec -it ai_interviewer_db psql -U postgres -d ai_interviewer
```

Then:

```sql
\d user_problems
SELECT * FROM user_problems LIMIT 20;
```

## Runtime behavior now

On every submit:

1. `submissions` row is created.
2. `user_problems` row is upserted for the same user/problem:
   - always updates `last_submission_at` and `last_submission_id`
   - on pass:
     - sets `is_passed = true`
     - sets `first_passed_at` only if it was `NULL`
