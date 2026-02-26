# String ID Migration

Use this after switching backend models/schemas to string IDs.

This migration converts:
- `users.id`
- `submissions.id`, `submissions.user_id`
- `testcases.id`
- `problem_list_problems.id`
- `user_problems.id`, `user_problems.user_id`, `user_problems.last_submission_id`

to `varchar(64)`.

## Apply

From repo root:

```bash
docker exec -i ai_interviewer_db psql -U postgres -d ai_interviewer < backend/docs/string_ids_migration.sql
```

## Verify

```bash
docker exec -it ai_interviewer_db psql -U postgres -d ai_interviewer
```

Then:

```sql
\d users
\d submissions
\d testcases
\d problem_list_problems
\d user_problems
```

You should see string ID columns (`character varying(64)`), and foreign keys reattached.
