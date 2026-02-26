-- Migration: convert remaining integer IDs/FKs to string IDs (PostgreSQL)
-- Run with:
-- docker exec -i ai_interviewer_db psql -U postgres -d ai_interviewer < backend/docs/string_ids_migration.sql

BEGIN;

-- Drop dependent foreign keys before changing column types.
ALTER TABLE submissions DROP CONSTRAINT IF EXISTS submissions_user_id_fkey;
ALTER TABLE user_problems DROP CONSTRAINT IF EXISTS user_problems_user_id_fkey;
ALTER TABLE user_problems DROP CONSTRAINT IF EXISTS user_problems_last_submission_id_fkey;

-- Remove serial defaults if they exist.
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE submissions DROP CONSTRAINT IF EXISTS submissions_pkey;
ALTER TABLE testcases DROP CONSTRAINT IF EXISTS testcases_pkey;
ALTER TABLE problem_list_problems DROP CONSTRAINT IF EXISTS problem_list_problems_pkey;
ALTER TABLE user_problems DROP CONSTRAINT IF EXISTS user_problems_pkey;

ALTER TABLE users ALTER COLUMN id DROP DEFAULT;
ALTER TABLE submissions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE testcases ALTER COLUMN id DROP DEFAULT;
ALTER TABLE problem_list_problems ALTER COLUMN id DROP DEFAULT;
ALTER TABLE user_problems ALTER COLUMN id DROP DEFAULT;

-- Convert PK and FK columns to varchar(64).
ALTER TABLE users ALTER COLUMN id TYPE VARCHAR(64) USING id::text;

ALTER TABLE submissions ALTER COLUMN id TYPE VARCHAR(64) USING id::text;
ALTER TABLE submissions ALTER COLUMN user_id TYPE VARCHAR(64) USING user_id::text;

ALTER TABLE testcases ALTER COLUMN id TYPE VARCHAR(64) USING id::text;

ALTER TABLE problem_list_problems ALTER COLUMN id TYPE VARCHAR(64) USING id::text;

ALTER TABLE user_problems ALTER COLUMN id TYPE VARCHAR(64) USING id::text;
ALTER TABLE user_problems ALTER COLUMN user_id TYPE VARCHAR(64) USING user_id::text;
ALTER TABLE user_problems ALTER COLUMN last_submission_id TYPE VARCHAR(64) USING last_submission_id::text;

-- Recreate primary keys.
ALTER TABLE users ADD CONSTRAINT users_pkey PRIMARY KEY (id);
ALTER TABLE submissions ADD CONSTRAINT submissions_pkey PRIMARY KEY (id);
ALTER TABLE testcases ADD CONSTRAINT testcases_pkey PRIMARY KEY (id);
ALTER TABLE problem_list_problems ADD CONSTRAINT problem_list_problems_pkey PRIMARY KEY (id);
ALTER TABLE user_problems ADD CONSTRAINT user_problems_pkey PRIMARY KEY (id);

-- Recreate dropped foreign keys.
ALTER TABLE submissions
    ADD CONSTRAINT submissions_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES users(id);

ALTER TABLE user_problems
    ADD CONSTRAINT user_problems_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES users(id);

ALTER TABLE user_problems
    ADD CONSTRAINT user_problems_last_submission_id_fkey
    FOREIGN KEY (last_submission_id) REFERENCES submissions(id);

COMMIT;
