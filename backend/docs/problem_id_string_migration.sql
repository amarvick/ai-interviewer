-- Migration: convert Problem IDs from integer -> string
-- Affects:
--   problems.id
--   submissions.problem_id
--   testcases.problem_id
--   problem_list_problems.problem_id
--
-- Run with:
-- docker exec -it ai_interviewer_db psql -U postgres -d ai_interviewer -f /Users/alexmarvick/Desktop/Personal/Programming/ai-interviewer/backend/docs/problem_id_string_migration.sql

BEGIN;

-- Drop foreign keys that depend on problems.id type.
ALTER TABLE submissions DROP CONSTRAINT IF EXISTS submissions_problem_id_fkey;
ALTER TABLE testcases DROP CONSTRAINT IF EXISTS testcases_problem_id_fkey;
ALTER TABLE problem_list_problems DROP CONSTRAINT IF EXISTS problem_list_problems_problem_id_fkey;

-- Remove legacy numeric default before type change.
ALTER TABLE problems ALTER COLUMN id DROP DEFAULT;

-- Convert primary and FK columns.
ALTER TABLE problems ALTER COLUMN id TYPE VARCHAR(64) USING id::text;
ALTER TABLE submissions ALTER COLUMN problem_id TYPE VARCHAR(64) USING problem_id::text;
ALTER TABLE testcases ALTER COLUMN problem_id TYPE VARCHAR(64) USING problem_id::text;
ALTER TABLE problem_list_problems ALTER COLUMN problem_id TYPE VARCHAR(64) USING problem_id::text;

-- Recreate foreign keys.
ALTER TABLE submissions
    ADD CONSTRAINT submissions_problem_id_fkey
    FOREIGN KEY (problem_id) REFERENCES problems(id);

ALTER TABLE testcases
    ADD CONSTRAINT testcases_problem_id_fkey
    FOREIGN KEY (problem_id) REFERENCES problems(id);

ALTER TABLE problem_list_problems
    ADD CONSTRAINT problem_list_problems_problem_id_fkey
    FOREIGN KEY (problem_id) REFERENCES problems(id);

COMMIT;

