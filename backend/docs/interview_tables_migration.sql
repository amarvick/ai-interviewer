-- Migration: add interview session tables
-- Run with:
-- docker exec -i ai_interviewer_db psql -U postgres -d ai_interviewer < backend/docs/interview_tables_migration.sql

BEGIN;

CREATE TABLE IF NOT EXISTS interview_sessions (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL REFERENCES users(id),
    problem_id VARCHAR(64) NOT NULL REFERENCES problems(id),
    stage VARCHAR(40) NOT NULL DEFAULT 'INTRO',
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    final_score DOUBLE PRECISION NULL,
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_interview_sessions_id ON interview_sessions (id);
CREATE INDEX IF NOT EXISTS ix_interview_sessions_user_id ON interview_sessions (user_id);
CREATE INDEX IF NOT EXISTS ix_interview_sessions_problem_id ON interview_sessions (problem_id);

CREATE TABLE IF NOT EXISTS interview_messages (
    id VARCHAR(64) PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL REFERENCES interview_sessions(id) ON DELETE CASCADE,
    user_id VARCHAR(64) NULL REFERENCES users(id),
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    stage_at_message VARCHAR(40) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_interview_messages_id ON interview_messages (id);
CREATE INDEX IF NOT EXISTS ix_interview_messages_session_id ON interview_messages (session_id);
CREATE INDEX IF NOT EXISTS ix_interview_messages_user_id ON interview_messages (user_id);

CREATE TABLE IF NOT EXISTS interview_evaluations (
    id VARCHAR(64) PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL REFERENCES interview_sessions(id) ON DELETE CASCADE,
    stage VARCHAR(40) NOT NULL,
    problem_understanding_score INTEGER NOT NULL DEFAULT 0 CHECK (problem_understanding_score BETWEEN 0 AND 2),
    approach_quality_score INTEGER NOT NULL DEFAULT 0 CHECK (approach_quality_score BETWEEN 0 AND 2),
    code_correctness_reasoning_score INTEGER NOT NULL DEFAULT 0 CHECK (code_correctness_reasoning_score BETWEEN 0 AND 2),
    complexity_analysis_score INTEGER NOT NULL DEFAULT 0 CHECK (complexity_analysis_score BETWEEN 0 AND 2),
    communication_clarity_score INTEGER NOT NULL DEFAULT 0 CHECK (communication_clarity_score BETWEEN 0 AND 2),
    total_score DOUBLE PRECISION NOT NULL DEFAULT 0,
    passed BOOLEAN NOT NULL DEFAULT FALSE,
    summary VARCHAR(500) NULL,
    rubric_json JSONB NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_interview_evaluations_id ON interview_evaluations (id);
CREATE INDEX IF NOT EXISTS ix_interview_evaluations_session_id ON interview_evaluations (session_id);

COMMIT;
