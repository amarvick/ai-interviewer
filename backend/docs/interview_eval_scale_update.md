# Interview Evaluation Scale Update

Use this migration to relax the per-category rubric constraints from `0-2` to `0-10`.

## Apply

```bash
docker exec -i ai_interviewer_db \
  psql -U postgres -d ai_interviewer \
  < backend/docs/interview_eval_scale_update.sql
```

Run it once after pulling this change. It drops the existing `ck_eval_*` constraints on `interview_evaluations` and re-creates them with the new bounds, fixing the integrity error when Gemini returns scores above 2.
