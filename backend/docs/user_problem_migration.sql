-- Migration: add user_problems progress table
-- Run with:
-- docker exec -i ai_interviewer_db psql -U postgres -d ai_interviewer < backend/docs/user_problem_migration.sql

BEGIN;

CREATE TABLE IF NOT EXISTS user_problems (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL REFERENCES users(id),
    problem_id VARCHAR(64) NOT NULL REFERENCES problems(id),
    is_passed BOOLEAN NOT NULL DEFAULT FALSE,
    first_passed_at TIMESTAMP NULL,
    last_submission_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_submission_id VARCHAR(64) NULL REFERENCES submissions(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_user_problem UNIQUE (user_id, problem_id)
);

CREATE INDEX IF NOT EXISTS ix_user_problems_user_id ON user_problems (user_id);
CREATE INDEX IF NOT EXISTS ix_user_problems_problem_id ON user_problems (problem_id);

COMMIT;
