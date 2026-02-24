-- Migration: attempts -> submissions (PostgreSQL)
-- Run inside psql connected to ai_interviewer DB.
-- Example:
-- docker exec -it ai_interviewer_db psql -U postgres -d ai_interviewer -f /path/to/submission_migration.sql

BEGIN;

-- If you have NO existing attempt data, this is the simplest path:
-- DROP TABLE IF EXISTS attempts CASCADE;
-- COMMIT;
-- Then start backend once so Base.metadata.create_all() creates "submissions".

-- If you MAY have data, do an in-place rename instead.
DO $$
BEGIN
    IF to_regclass('public.attempts') IS NOT NULL
       AND to_regclass('public.submissions') IS NULL THEN
        EXECUTE 'ALTER TABLE attempts RENAME TO submissions';
    END IF;
END $$;

-- Optional cleanup: rename legacy sequence/index names if they exist.
DO $$
BEGIN
    IF to_regclass('public.attempts_id_seq') IS NOT NULL
       AND to_regclass('public.submissions_id_seq') IS NULL THEN
        EXECUTE 'ALTER SEQUENCE attempts_id_seq RENAME TO submissions_id_seq';
    END IF;
END $$;

DO $$
BEGIN
    IF to_regclass('public.ix_attempts_id') IS NOT NULL
       AND to_regclass('public.ix_submissions_id') IS NULL THEN
        EXECUTE 'ALTER INDEX ix_attempts_id RENAME TO ix_submissions_id';
    END IF;
END $$;

-- Ensure submissions.language exists for code execution/runtime selection.
DO $$
BEGIN
    IF to_regclass('public.submissions') IS NOT NULL
       AND NOT EXISTS (
           SELECT 1
           FROM information_schema.columns
           WHERE table_schema = 'public'
             AND table_name = 'submissions'
             AND column_name = 'language'
       ) THEN
        EXECUTE 'ALTER TABLE submissions ADD COLUMN language VARCHAR(20)';
        EXECUTE 'UPDATE submissions SET language = ''python'' WHERE language IS NULL';
        EXECUTE 'ALTER TABLE submissions ALTER COLUMN language SET NOT NULL';
    END IF;
END $$;

DO $$
BEGIN
    IF to_regclass('public.ix_submissions_language') IS NULL
       AND EXISTS (
           SELECT 1
           FROM information_schema.columns
           WHERE table_schema = 'public'
             AND table_name = 'submissions'
             AND column_name = 'language'
       ) THEN
        EXECUTE 'CREATE INDEX ix_submissions_language ON submissions (language)';
    END IF;
END $$;

COMMIT;
