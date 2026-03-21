# SMART PARENTING — Module 1 Database Implementation Plan

**For:** ETEST ONE
**Scope:** Module 1 — Smart Parenting only (PostgreSQL)
**Status:** Draft
**Stack:** PostgreSQL + Alembic migrations + FastAPI (Python) + SQLAlchemy 2.0 (asyncpg)
**Demo Subject:** Nguyễn Hà Minh Anh · Cô Thu

> **⚠️ Backend note:** The actual codebase (`e-be/`) uses **FastAPI (Python)** with SQLAlchemy 2.0 async (`asyncpg`). Alembic manages migrations. All repository functions, route handlers, and test scripts below use **Python/async SQLAlchemy** — not Node.js.

---

## Table of Contents

1. [Schema Design Principles](#1-schema-design-principles)
2. [PostgreSQL Table Schemas](#2-postgresql-table-schemas)
3. [Indexes — Purpose & Design](#3-indexes--purpose--design)
4. [Pre-Aggregated / Trigger-Maintained Columns](#4-pre-aggregated--trigger-maintained-columns)
5. [Seed SQL — Demo Scenario](#5-seed-sql--demo-scenario)
6. [Implementation Order (aligned H0–H3)](#6-implementation-order-aligned-h0-h3)
7. [Notes & Edge Cases](#7-notes--edge-cases)

---

## 1. Schema Design Principles

| Principle | Application |
|---|---|
| **3 role tables, no generic users** | `parents`, `students`, `mentors` are the only identity tables. No shared `users` table — each role has its own typed table with role-specific fields. |
| **1:1 Parent–Student enforced in DB** | `students.parent_id` has a `UNIQUE NOT NULL` constraint. A DB-level `EXCLUDE` constraint prevents any parent from having two students. |
| **Natural primary keys where possible** | `student_id` (e.g. `STU_001`), `parent_id`, `mentor_id` as natural strings — no surrogate UUIDs for entity tables. |
| **Dates as `DATE`, times as `TIME`** | `behavioral_logs.date` is `DATE`. `session_start` / `session_end` are `TIME`. Separating date from time avoids timezone ambiguity for daily records. |
| **JSON for semi-structured data** | `skill_breakdown`, `target_schools`, `context_snapshot`, `ai_summary` stored as `JSONB` — queryable with `->` operator, indexable with GIN. |
| **Triggers for pre-aggregated columns** | `progress_pct`, `milestones_done`, `next_deadline`, `days_left`, `priority_action` on `students` are maintained by PostgreSQL triggers on `milestones` INSERT/UPDATE/DELETE — zero application-side recalculation needed. |
| **Alembic for migration management** | All schema changes versioned in `alembic/versions/` — `alembic upgrade head` applies all pending migrations; `alembic downgrade -1` rolls back cleanly. `target_metadata = None` (raw SQL, no ORM models). |
| **30-day TTL for conversations** | An `expires_at TIMESTAMPTZ` column + nightly cron job: `DELETE FROM conversations WHERE expires_at < NOW()`. No application-level TTL logic needed. |
| **Partial indexes for common filters** | e.g. `WHERE status = 'upcoming'` for deadline queries — half the size of a full index. |

---

## 2. PostgreSQL Table Schemas

### 2.1 · `parents`

Authentication and profile for parent accounts. The primary actor in Smart Parenting (viewing the dashboard, chatting with AI, receiving alerts).

```sql
CREATE TABLE parents (
    parent_id       SERIAL PRIMARY KEY,

    -- Auth
    email           VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,

    -- Profile
    full_name       VARCHAR(255) NOT NULL,                        -- e.g. "Cô Thu"
    phone           VARCHAR(50),
    telegram_id     VARCHAR(100),

    -- 1:1 link to the single child managed by this parent
    -- UNIQUE + NOT NULL enforces the constraint at DB level
    student_id      VARCHAR(50)  NOT NULL UNIQUE,

    created_at      TIMESTAMPT   NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPT   NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_parents_student_id ON parents (student_id);     -- resolve parent from student_id
CREATE INDEX idx_parents_email       ON parents (email);          -- auth: login lookup
```

**Access Pattern:** `SELECT … FROM parents WHERE parent_id = :id` → fetch profile for chat header.

**Constraint check (requires btree_gist):**

```sql
-- Redundant with UNIQUE, but explicit; prevents any student from being
-- linked to more than one parent row even if multi-parent support is added later.
ALTER TABLE parents ADD CONSTRAINT chk_one_parent_per_student
    EXCLUDE USING gist (student_id WITH =);
```

---

### 2.2 · `students`

Core learner profile. `parent_id` is **unique + not null** — enforces the 1:1 constraint at DB level. `mentor_id` is nullable (a mentor can advise many students).

```sql
CREATE TABLE students (
    student_id     VARCHAR(50)   PRIMARY KEY,                     -- e.g. "STU_001"

    -- Identity
    name           VARCHAR(255)  NOT NULL,

    -- Academic scores
    ielts_score    DECIMAL(4,1),
    sat_score      DECIMAL(5,1),
    gpa            DECIMAL(4,2),

    -- Semi-structured JSON
    skill_breakdown JSONB,                                        -- {"listening":7.0,"reading":7.0,"writing":5.5,"speaking":6.5}
    target_schools  JSONB,                                       -- ["University of Melbourne", "UNSW Sydney", "Monash"]

    -- Program
    program         VARCHAR(100),
    months_enrolled INTEGER      DEFAULT 0,

    -- Role links
    parent_id       INTEGER      NOT NULL UNIQUE
                    REFERENCES parents(parent_id)
                    ON DELETE RESTRICT,
    mentor_id       INTEGER      REFERENCES mentors(mentor_id)
                    ON DELETE SET NULL,

    created_at      TIMESTAMPT   NOT NULL DEFAULT NOW(),

    -- ── Pre-aggregated digest columns (maintained by triggers) ──────────────
    progress_pct        SMALLINT   DEFAULT 0 CHECK (progress_pct BETWEEN 0 AND 100),
    milestones_done     SMALLINT   DEFAULT 0,
    next_deadline       DATE,
    next_deadline_label VARCHAR(255),
    days_left           SMALLINT,
    priority_action     VARCHAR(255),

    -- ── Wellbeing context (updated by app on behavioural log write) ─────────
    current_streak     SMALLINT   DEFAULT 0,
    last_activity_date DATE,

    -- ── Upsell guard ────────────────────────────────────────────────────────
    upsell_cooldown    DATE       DEFAULT (CURRENT_DATE - INTERVAL '1 day')   -- always expired on first load
);

CREATE INDEX idx_students_parent_id ON students (parent_id);    -- auth: resolve student from parent
CREATE INDEX idx_students_mentor_id  ON students (mentor_id);    -- filter students by assigned mentor
CREATE INDEX idx_students_program    ON students (program);      -- filter by program (AMP / IELTS / SAT)
```

> **PostgreSQL note:** The `EXCLUDE` constraint requires the `btree_gist` extension. Install with: `CREATE EXTENSION IF NOT EXISTS btree_gist;`

---

### 2.3 · `mentors`

Mentor profiles. A mentor can be assigned to multiple students (1 mentor : N students). `mentor_id` is the primary key referenced from `students.mentor_id`.

```sql
CREATE TABLE mentors (
    mentor_id       SERIAL PRIMARY KEY,

    -- Auth
    email           VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,

    -- Profile
    full_name       VARCHAR(255) NOT NULL,                        -- e.g. "Cô Lan — Mentor AMP"
    specialty       VARCHAR(255),                                 -- e.g. "IELTS Writing, SAT Math"
    bio             TEXT,
    avatar_url      VARCHAR(500),

    -- Which programs they can mentor
    programs        JSONB,                                         -- ["AMP", "IELTS", "SAT"]
    max_students    SMALLINT    DEFAULT 10,

    -- Analytics (maintained by application or triggers)
    active_students SMALLINT    DEFAULT 0,

    created_at      TIMESTAMPT   NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPT   NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_mentors_email    ON mentors (email);             -- auth: login lookup
CREATE INDEX idx_mentors_programs ON mentors USING GIN (programs); -- find mentors by program
```

---

### 2.4 · `courses`

ETEST upsell catalog. Links to `students` via the upsell engine to recommend relevant courses/camps based on student skill gaps and program.

```sql
CREATE TABLE courses (
    course_id       SERIAL PRIMARY KEY,

    -- Identity
    name            VARCHAR(255) NOT NULL,                        -- e.g. "IELTS Writing Intensive — June Camp"
    slug            VARCHAR(255) NOT NULL UNIQUE,                  -- URL-friendly, e.g. "ielts-writing-intensive-june-camp"

    -- Classification
    type            VARCHAR(50)  NOT NULL
                    CHECK (type IN ('camp', 'workshop', 'course')),
    program         VARCHAR(100),                                  -- "AMP", "IELTS", "SAT", or NULL if multi-program
    season          VARCHAR(50),                                   -- "Summer 2026", "Spring 2026", "All Year"

    -- Content
    description     TEXT,
    target_skills   JSONB,                                         -- ["IELTS_Writing", "Essay_Structure"]
    suitable_for     JSONB,                                         -- ["student_gap_writing", "student_target_7plus"]
    cta_url         VARCHAR(500),                                   -- landing page or registration link
    cta_label       VARCHAR(100),                                   -- "Đăng ký ngay", "Xem chi tiết"

    -- Logistics
    duration_days   SMALLINT,
    start_date      DATE,
    end_date        DATE,
    location        VARCHAR(255),                                   -- "Online", "Hồ Chí Minh", "Hà Nội"
    price_vnd       BIGINT,

    -- Display
    is_featured     BOOLEAN    DEFAULT FALSE,
    is_active       BOOLEAN    DEFAULT TRUE,
    display_order   SMALLINT   DEFAULT 0,

    created_at      TIMESTAMPT  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPT  NOT NULL DEFAULT NOW()
);

-- Find courses by skill gap (JSONB containment)
CREATE INDEX idx_courses_target_skills  ON courses USING GIN (target_skills);
-- Find courses by suitable-for tags
CREATE INDEX idx_courses_suitable_for   ON courses USING GIN (suitable_for);
-- Find active courses by program + season
CREATE INDEX idx_courses_program_season ON courses (program, season)
    WHERE is_active = TRUE;
```

---

### 2.5 · `behavioral_logs`

One row per student per calendar date. Key table for the 14-day wellbeing engine.

```sql
CREATE TABLE behavioral_logs (
    id             SERIAL PRIMARY KEY,

    student_id     VARCHAR(50)  NOT NULL REFERENCES students(student_id)
                   ON DELETE CASCADE,

    date           DATE         NOT NULL,               -- "YYYY-MM-DD"

    duration_min   SMALLINT,                             -- total study minutes
    session_start  TIME,                                 -- "HH:MM:SS"
    session_end    TIME,                                 -- derived on insert
    studied        BOOLEAN      DEFAULT FALSE,

    streak_day     SMALLINT     DEFAULT 0,               -- consecutive study days
    score_delta    DECIMAL(4,1) DEFAULT 0,               -- IELTS band change vs last mock

    -- Computed at insert time — saves a scan in wellbeing engine
    is_late_night  BOOLEAN      GENERATED ALWAYS AS
                   (session_start >= '22:00:00') STORED,

    -- JSON list of activity tags
    activities     JSONB,                                 -- ["ielts_mock","essay_draft"]
    mood_note      TEXT,                                  -- optional student self-report

    created_at     TIMESTAMPT    NOT NULL DEFAULT NOW(),

    -- Unique per student per day (upsert pattern)
    UNIQUE (student_id, date)
);

-- Composite index: student + date descending → covers 14-day wellbeing query
CREATE INDEX idx_behavioral_logs_student_date
    ON behavioral_logs (student_id, date DESC);

-- Partial index: only studied days (for streak / avg duration)
CREATE INDEX idx_behavioral_logs_studied
    ON behavioral_logs (student_id, date DESC)
    WHERE studied = TRUE;
```

**Design Notes:**
- `is_late_night` is a **generated column** (PostgreSQL 12+) — computed once at insert, stored, zero runtime cost.
- `session_end` can be derived from `session_start + duration_min` at the application layer; store it if the backend reads it directly.
- The `UNIQUE (student_id, date)` constraint enforces one log per student per day — upsert with `ON CONFLICT (student_id, date) DO UPDATE`.

---

### 2.6 · `conversations`

30-day chat history. `expires_at` drives the nightly TTL cleanup job.

```sql
CREATE TABLE conversations (
    id              SERIAL PRIMARY KEY,

    parent_id       INTEGER      NOT NULL REFERENCES parents(parent_id)
                    ON DELETE CASCADE,
    student_id      VARCHAR(50)  NOT NULL REFERENCES students(student_id)
                    ON DELETE CASCADE,

    timestamp       TIMESTAMPT   NOT NULL DEFAULT NOW(),
    question        TEXT         NOT NULL,
    ai_response     TEXT         NOT NULL,

    -- Snapshot of student state at conversation time — critical for AI fidelity
    context_snapshot JSONB,                               -- {
                                                          --   "student_name":"Nguyễn Hà Minh Anh",
                                                          --   "ielts_score":6.5,
                                                          --   "target_schools":[...],
                                                          --   "progress_pct":68,
                                                          --   "weakest_skill":"Writing",
                                                          --   "next_deadline":"2026-05-07"
                                                          -- }

    escalated       BOOLEAN      DEFAULT FALSE,
    escalator_note  TEXT,

    -- 30-day TTL: set expires_at = timestamp + 30 days on insert
    expires_at      TIMESTAMPT,

    created_at      TIMESTAMPT   NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversations_parent_timestamp
    ON conversations (parent_id, timestamp DESC);        -- 30-day history for AI context

CREATE INDEX idx_conversations_student_id
    ON conversations (student_id, timestamp DESC);       -- admin audit

CREATE INDEX idx_conversations_expires_at
    ON conversations (expires_at)
    WHERE expires_at IS NOT NULL;                         -- TTL cleanup: DELETE WHERE expires_at < NOW()
```

---

### 2.7 · `milestones`

Achievement and upcoming goal records. The primary driver of all pre-aggregated digest fields on `students`.

```sql
CREATE TABLE milestones (
    id              SERIAL PRIMARY KEY,

    student_id      VARCHAR(50)  NOT NULL REFERENCES students(student_id)
                    ON DELETE CASCADE,
    milestone_id    VARCHAR(100) NOT NULL,                -- "ms_001" — human-readable, sortable

    type            VARCHAR(50)  NOT NULL
                    CHECK (type IN (
                        'ielts_mock','essay_draft','essay_final',
                        'sat_mock','extracurricular','consultation',
                        'camp','csr','target_achieved'
                    )),
    title           VARCHAR(255) NOT NULL,
    date            DATE         NOT NULL,

    score           DECIMAL(5,2),                           -- numeric score if applicable (6.5, 1320, etc.)
    score_label     VARCHAR(100),                          -- "IELTS Band 6.5"

    mentor_id       INTEGER      REFERENCES mentors(mentor_id) ON DELETE SET NULL,
    mentor_approved BOOLEAN,
    auth_score      SMALLINT     CHECK (auth_score BETWEEN 0 AND 100),  -- 0–100, null if not essay

    notes           TEXT,

    status          VARCHAR(20)  NOT NULL DEFAULT 'upcoming'
                    CHECK (status IN ('completed', 'in_progress', 'upcoming')),

    contributor_type VARCHAR(50) NOT NULL DEFAULT 'student'
                    CHECK (contributor_type IN (
                        'student','mentor','parent','institution'
                    )),

    ai_summary      JSONB,                                -- {"summary":"...", "skills_demonstrated":[...],"evidence_strength":"high"}

    created_at      TIMESTAMPT    NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPT    NOT NULL DEFAULT NOW(),

    -- Unique milestone_id within a student's scope
    UNIQUE (student_id, milestone_id)
);

CREATE INDEX idx_milestones_student_date
    ON milestones (student_id, date DESC);                -- full timeline for StudentProgress

CREATE INDEX idx_milestones_student_status
    ON milestones (student_id, status, date ASC)
    WHERE status IN ('completed', 'upcoming');            -- covers progress_pct + next_deadline queries

-- Partial index: upcoming only, sorted by date → next_deadline scan
CREATE INDEX idx_milestones_upcoming
    ON milestones (student_id, date ASC)
    WHERE status = 'upcoming';

-- Partial index: completed only → milestones_done count
CREATE INDEX idx_milestones_completed
    ON milestones (student_id, date DESC)
    WHERE status = 'completed';

-- Partial index: essay milestones with auth_score → authenticity check
CREATE INDEX idx_milestones_essays
    ON milestones (student_id, date DESC)
    WHERE type IN ('essay_draft', 'essay_final')
      AND auth_score IS NOT NULL;
```

---

## 3. Indexes — Purpose & Design

| Index | Table | Columns | Type | Purpose |
|---|---|---|---|---|
| `idx_parents_student_id` | `parents` | `student_id` | B-tree | **Auth anchor** — resolve parent from their child's `student_id` in one seek. Used when student-driven events need to notify the parent. |
| `idx_parents_email` | `parents` | `email` | B-tree | Login: `SELECT … FROM parents WHERE email = :email`. |
| `idx_students_parent_id` | `students` | `parent_id` | B-tree | **Auth anchor** — resolve the single linked student from the authenticated `parent_id`. Core H1 query. |
| `idx_students_mentor_id` | `students` | `mentor_id` | B-tree | Mentor dashboard: list all students assigned to a mentor. |
| `idx_students_program` | `students` | `program` | B-tree | Filter by AMP / IELTS / SAT program (future cohort queries). |
| `idx_mentors_email` | `mentors` | `email` | B-tree | Mentor login. |
| `idx_mentors_programs` | `mentors` | `programs` | GIN | Find mentors who can advise a specific program (e.g. `WHERE programs @> '"AMP"'`). |
| `idx_courses_target_skills` | `courses` | `target_skills` | GIN | **Upsell engine** — find courses covering specific skill gaps: `WHERE target_skills @> '["IELTS_Writing"]'`. |
| `idx_courses_suitable_for` | `courses` | `suitable_for` | GIN | **Upsell engine** — match courses by student profile tags: `WHERE suitable_for @> '["student_gap_writing"]'`. |
| `idx_courses_program_season` | `courses` | `(program, season)` | B-tree | **Upsell catalog** — filter active courses by program + timing in one seek. |
| `idx_behavioral_logs_student_date` | `behavioral_logs` | `(student_id, date DESC)` | B-tree | **Wellbeing engine** — `SELECT … WHERE student_id = :id AND date >= :start ORDER BY date DESC`. Covers the full 14-day window. |
| `idx_behavioral_logs_studied` | `behavioral_logs` | `(student_id, date DESC)` | Partial | **Streak / avg duration** — only studied days. Reduces index size by excluding non-study rows. |
| `idx_conversations_parent_timestamp` | `conversations` | `(parent_id, timestamp DESC)` | B-tree | **30-day chat history** — `SELECT … WHERE parent_id = :id AND timestamp >= :start ORDER BY timestamp DESC`. |
| `idx_conversations_student_id` | `conversations` | `(student_id, timestamp DESC)` | B-tree | Admin audit: all conversations about a student across all parents. |
| `idx_conversations_expires_at` | `conversations` | `expires_at` | Partial | **TTL cleanup** — `DELETE FROM conversations WHERE expires_at < NOW()`. Small partial index over only non-null expires_at rows. |
| `idx_milestones_student_date` | `milestones` | `(student_id, date DESC)` | B-tree | **StudentProgress timeline** — chronological list regardless of status. |
| `idx_milestones_student_status` | `milestones` | `(student_id, status, date ASC)` | Partial | **Digest card queries** — filter by status + date. Covers `progress_pct` (completed count) and upcoming deadline sort. |
| `idx_milestones_upcoming` | `milestones` | `(student_id, date ASC)` | Partial | **next_deadline** — `MIN(date) WHERE status = 'upcoming'` in a single seek. |
| `idx_milestones_completed` | `milestones` | `(student_id, date DESC)` | Partial | **milestones_done count** — `COUNT WHERE status = 'completed'` in an index-only scan. |
| `idx_milestones_essays` | `milestones` | `(student_id, date DESC)` | Partial | **Authenticity scoring** — fetch writing history for essay scoring. Only essay-type rows. |

### Why PostgreSQL indexes beat DynamoDB GSIs here

- **No write amplification:** GSI writes in DynamoDB count toward both base-table and GSI write capacity — cost doubles for every index. PostgreSQL B-tree indexes have no write amplification.
- **Partial indexes:** A PostgreSQL partial index stores only the rows that matter (e.g. `WHERE status = 'upcoming'`) — DynamoDB would need a full GSI scan.
- **Composite index covers both order and filter:** A single `(student_id, date DESC)` index handles `WHERE student_id = ? ORDER BY date DESC` without a separate sort step.
- **No hot partition risk:** DynamoDB PK hot spots on a single student's partition are eliminated. PostgreSQL's buffer pool handles concurrent reads naturally.

---

## 4. Pre-Aggregated / Trigger-Maintained Columns

All five digest fields on `students` are **maintained by a single PostgreSQL trigger function** on `milestones`. No application-side recalculation needed on reads.

### 4.1 Trigger Function

```sql
CREATE OR REPLACE FUNCTION sync_student_digest_from_milestones()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    v_next              RECORD;
    v_completed_count   SMALLINT;
    v_total_count       SMALLINT;
    v_progress          SMALLINT;
BEGIN
    IF TG_OP = 'DELETE' THEN
        -- Student_id lives in OLD for DELETE
    END IF;

    -- ── Count completed and total milestones ───────────────────────────────
    SELECT
        COUNT(*) FILTER (WHERE status = 'completed') AS completed,
        COUNT(*)                                       AS total
    INTO v_completed_count, v_total_count
    FROM milestones
    WHERE student_id = COALESCE(NEW.student_id, OLD.student_id);

    -- ── Compute progress_pct ───────────────────────────────────────────────
    IF v_total_count > 0 THEN
        v_progress := LEAST(100, (v_completed_count::SMALLINT * 100) / v_total_count);
    ELSE
        v_progress := 0;
    END IF;

    -- ── Find nearest upcoming milestone (next_deadline) ────────────────────
    SELECT date, title
    INTO v_next
    FROM milestones
    WHERE student_id   = COALESCE(NEW.student_id, OLD.student_id)
      AND status       = 'upcoming'
      AND date        >= CURRENT_DATE
    ORDER BY date ASC
    LIMIT 1;

    -- ── Update students row ────────────────────────────────────────────────
    UPDATE students SET
        milestones_done     = v_completed_count,
        progress_pct        = v_progress,
        next_deadline       = v_next.date,
        next_deadline_label = v_next.title,
        days_left           = CASE
                                  WHEN v_next.date IS NOT NULL
                                  THEN (v_next.date - CURRENT_DATE)::SMALLINT
                                  ELSE NULL
                              END,
        priority_action    = CASE
                                  WHEN v_next.title IS NOT NULL
                                  THEN 'Hoàn thành: ' || v_next.title
                                  ELSE NULL
                              END
    WHERE student_id = COALESCE(NEW.student_id, OLD.student_id);

    RETURN COALESCE(NEW, OLD);
END;
$$;
```

### 4.2 Trigger Attachment

```sql
CREATE TRIGGER trg_milestones_sync_digest
    AFTER INSERT OR UPDATE OF status, date ON milestones
    REFERENCING NEW TABLE AS NEW OLD TABLE AS OLD
    FOR EACH STATEMENT EXECUTE FUNCTION sync_student_digest_from_milestones();
```

> **PostgreSQL 15+ syntax** — `REFERENCING OLD TABLE AS OLD` is required for `AFTER … ON milestones` statement-level triggers that need to read `OLD` rows. For older PG versions, use a row-level `FOR EACH ROW` trigger instead.

### 4.3 Pre-Aggregated Fields on `students` — Summary

| Column | Type | Updated When | Method |
|---|---|---|---|
| `progress_pct` | `SMALLINT` | Any milestone insert/update/delete | Trigger recalculates ratio |
| `milestones_done` | `SMALLINT` | Any milestone insert where `status = 'completed'` | Trigger COUNT |
| `next_deadline` | `DATE` | Any upcoming milestone insert/update | Trigger `MIN(date) WHERE upcoming` |
| `next_deadline_label` | `VARCHAR(255)` | Same as above | Trigger copies `title` |
| `days_left` | `SMALLINT` | Same as above | Trigger `(next_deadline - CURRENT_DATE)::SMALLINT` |
| `priority_action` | `VARCHAR(255)` | Same as above | Trigger `'Hoàn thành: ' || title` |
| `current_streak` | `SMALLINT` | App writes new `behavioral_log` | Maintained in application layer on log upsert (too complex for a milestone trigger) |
| `last_activity_date` | `DATE` | App upserts `behavioral_log` | Application writes on each log save |
| `is_late_night` | `BOOLEAN` | App writes `behavioral_log` | PostgreSQL generated column — zero cost |

### 4.4 `days_left` — On-Read Alternative

`days_left` changes every 24 hours. Computing it at read time is also trivial:

```sql
SELECT
    student_id,
    next_deadline,
    (next_deadline - CURRENT_DATE) AS days_left,
    priority_action
FROM students
WHERE student_id = 'STU_001';
```

PostgreSQL computes the date difference at query time — no application logic needed. Either approach works; the stored column is preferred for this plan since it keeps the digest card response as a **single-row select with no computation**.

---

## 5. Seed SQL — Demo Scenario

**Scenario:** Nguyễn Hà Minh Anh · AMP · 14 tháng · IELTS 6.5 · SAT 1320
**Parent:** Cô Thu (`parents.parent_id = 1`)
**Mentor:** Cô Lan (`mentors.mentor_id = 1`)
**Trigger:** 3 late nights Mar 17–20 · streak break Mar 11→12 · EA deadline May 7 2026
**Seed date:** 2026-03-21

### 5.1 Prerequisites

```sql
-- Enable extension for 1:1 exclude constraint (run once per database)
CREATE EXTENSION IF NOT EXISTS btree_gist;
```

### 5.2 Mentors (must exist before students — FK dependency)

```sql
INSERT INTO mentors
    (mentor_id, email, hashed_password, full_name, specialty, bio, programs, max_students, active_students, created_at)
VALUES
    (1,
     'co-lan@etest.vn',
     '$2b$12$dummy.hash.for.seed.only',
     'Cô Lan',
     'IELTS Writing, Academic Essay, Personal Statement',
     'Mentor 5 năm kinh nghiệm, chuyên gia luyện IELTS và hồ sơ du học Australia.',
     '["AMP", "IELTS"]'::jsonb,
     10, 1,
     '2024-09-01T00:00:00+07:00'
    )
ON CONFLICT (mentor_id) DO UPDATE SET
    full_name       = EXCLUDED.full_name,
    active_students = EXCLUDED.active_students;

ALTER SEQUENCE mentors_mentor_id_seq RESTART WITH 2;
```

### 5.3 Parents (must exist before students — FK dependency)

```sql
INSERT INTO parents
    (parent_id, email, hashed_password, full_name, phone, student_id, created_at)
VALUES
    (1,
     'co-thu@example.com',
     '$2b$12$dummy.hash.for.seed.only',
     'Cô Thu',
     '+84-90-123-4567',
     'STU_001',
     '2024-09-01T00:00:00+07:00'
    )
ON CONFLICT (parent_id) DO UPDATE SET full_name = EXCLUDED.full_name;

ALTER SEQUENCE parents_parent_id_seq RESTART WITH 2;
```

### 5.4 Students

```sql
INSERT INTO students (
    student_id, name,
    ielts_score, sat_score, gpa,
    skill_breakdown, target_schools,
    program, months_enrolled,
    parent_id, mentor_id,
    progress_pct, milestones_done,
    next_deadline, next_deadline_label, days_left, priority_action,
    current_streak, last_activity_date,
    upsell_cooldown,
    created_at
) VALUES (
    'STU_001',
    'Nguyễn Hà Minh Anh',
    6.5, 1320.0, 8.4,
    '{"listening": 7.0, "reading": 7.0, "writing": 5.5, "speaking": 6.5}'::jsonb,
    '["University of Melbourne", "UNSW Sydney", "Monash University"]'::jsonb,
    'AMP', 14,
    1, 1,                                                -- Cô Thu (parent_id=1) + Cô Lan (mentor_id=1)
    68, 12,
    '2026-05-07', 'Nộp hồ sơ Early Action', 47, 'Hoàn thành: Personal Statement Final v2 (Melbourne)',
    3, '2026-03-20',
    '2026-03-28',
    '2024-09-01T00:00:00+07:00'
) ON CONFLICT (student_id) DO UPDATE SET
    progress_pct        = EXCLUDED.progress_pct,
    milestones_done     = EXCLUDED.milestones_done,
    next_deadline       = EXCLUDED.next_deadline,
    next_deadline_label = EXCLUDED.next_deadline_label,
    days_left           = EXCLUDED.days_left,
    priority_action     = EXCLUDED.priority_action,
    current_streak      = EXCLUDED.current_streak,
    last_activity_date  = EXCLUDED.last_activity_date,
    upsell_cooldown     = EXCLUDED.upsell_cooldown;
```

### 5.5 Behavioral Logs — 14 items (2026-03-08 → 2026-03-21)

```sql
INSERT INTO behavioral_logs
    (student_id, date, duration_min, session_start, session_end, studied, streak_day, score_delta, activities, mood_note)
VALUES
    -- Mar 21 — today, normal session
    ('STU_001', '2026-03-21', 75,  '21:00', '22:15', TRUE, 3,  0.0, '["essay_draft"]'::jsonb,                NULL),
    -- Mar 20 — LATE NIGHT (23:15)
    ('STU_001', '2026-03-20', 110, '23:15', '01:05', TRUE, 2,  0.0, '["ielts_mock","essay_draft"]'::jsonb,  NULL),
    -- Mar 19 — LATE NIGHT (23:40)
    ('STU_001', '2026-03-19', 95,  '23:40', '01:15', TRUE, 1,  0.0, '["ielts_practice"]'::jsonb,            NULL),
    -- Mar 18 — LATE NIGHT (22:30)
    ('STU_001', '2026-03-18', 100, '22:30', '00:10', TRUE, 8,  0.5, '["sat_math","reading"]'::jsonb,        NULL),
    -- Mar 17 — normal, streak intact
    ('STU_001', '2026-03-17', 80,  '20:00', '21:20', TRUE, 7,  0.0, '["speaking_practice"]'::jsonb,         NULL),
    -- Mar 16
    ('STU_001', '2026-03-16', 60,  '19:30', '20:30', TRUE, 6,  0.0, '["listening"]'::jsonb,                  NULL),
    -- Mar 15
    ('STU_001', '2026-03-15', 90,  '20:15', '21:45', TRUE, 5,  0.0, '["writing_task1"]'::jsonb,            NULL),
    -- Mar 14
    ('STU_001', '2026-03-14', 85,  '19:00', '20:25', TRUE, 4,  0.0, '["reading_comprehension"]'::jsonb,   NULL),
    -- Mar 13
    ('STU_001', '2026-03-13', 70,  '20:30', '21:40', TRUE, 3,  0.0, '["vocabulary"]'::jsonb,               NULL),
    -- Mar 12
    ('STU_001', '2026-03-12', 95,  '21:00', '22:35', TRUE, 2,  0.0, '["sat_math"]'::jsonb,                 NULL),
    -- Mar 11
    ('STU_001', '2026-03-11', 80,  '19:45', '21:05', TRUE, 1,  0.0, '["speaking_mock"]'::jsonb,             NULL),
    -- Mar 10 — streak 8 (last high point before break)
    ('STU_001', '2026-03-10', 110, '20:00', '21:50', TRUE, 8,  0.0, '["ielts_mock","essay_review"]'::jsonb, NULL),
    -- Mar 9
    ('STU_001', '2026-03-09', 75,  '19:30', '20:45', TRUE, 7,  0.0, '["writing_task2"]'::jsonb,             NULL),
    -- Mar 8
    ('STU_001', '2026-03-08', 60,  '20:00', '21:00', TRUE, 6,  0.0, '["reading"]'::jsonb,                   NULL)
ON CONFLICT (student_id, date) DO UPDATE SET
    duration_min  = EXCLUDED.duration_min,
    session_start = EXCLUDED.session_start,
    session_end   = EXCLUDED.session_end,
    studied       = EXCLUDED.studied,
    streak_day    = EXCLUDED.streak_day,
    score_delta   = EXCLUDED.score_delta,
    activities    = EXCLUDED.activities;
```

**Wellbeing trigger analysis from this seed:**

| Period | Avg Duration | Late Nights | Streak Note |
|---|---|---|---|
| Mar 8–14 (7 days) | ~83 min/day | 0 | Streak peaks at 8, then breaks (Mar 11→12) |
| Mar 15–21 (7 days) | ~84 min/day | 3 (Mar 18, 19, 20) | Streak reset to 1 then rebuilt to 3 |
| **Result** | Stable | **3 late nights in 4 days — HIGH severity** | Streak break detected |

Expected wellbeing alert: **severity HIGH** — late-night pattern (≥2 sessions after 22:00 in 5 days) + streak break.

### 5.6 Milestones — 15 items (12 completed + 3 upcoming)

```sql
INSERT INTO milestones
    (student_id, milestone_id, type, title, date, score, score_label,
     mentor_id, mentor_approved, auth_score, notes, status, contributor_type)
VALUES
    -- ── Completed ──────────────────────────────────────────────────────────
    ('STU_001','ms_001','ielts_mock',        'IELTS Mock #1 — Overall 5.5',          '2024-10-15', 5.5,  'IELTS Band 5.5',   1, TRUE,  NULL, NULL,                              'completed',  'student'),
    ('STU_001','ms_002','essay_draft',        'Personal Statement Draft #1',          '2024-11-20', NULL, 'Draft',            1, FALSE, 82,  NULL,                              'completed',  'student'),
    ('STU_001','ms_003','ielts_mock',        'IELTS Mock #2 — Overall 6.0',          '2024-12-10', 6.0,  'IELTS Band 6.0',   1, TRUE,  NULL, NULL,                              'completed',  'student'),
    ('STU_001','ms_004','essay_final',        'Personal Statement Final v1',          '2025-01-15', NULL, 'Final',            1, TRUE,  88, 'Minh Anh thể hiện rõ giọng văn cá nhân.','completed','student'),
    ('STU_001','ms_005','sat_mock',          'SAT Mock #1',                           '2025-02-20', 1250, 'SAT 1250',         1, TRUE,  NULL, NULL,                              'completed',  'student'),
    ('STU_001','ms_006','extracurricular',   'ETEST CSR — Dạy tiếng Anh trẻ em',     '2025-03-10', NULL, 'Hoạt động',        1, TRUE,  NULL, 'Tham gia tích cực, được phụ huynh ghi nhận.','completed','student'),
    ('STU_001','ms_007','consultation',      'Tư vấn lộ trình AMP',                  '2025-03-25', NULL, 'Consultation',     1, TRUE,  NULL, 'Cô Thu tham dự cùng con.',                  'completed',  'parent'),
    ('STU_001','ms_008','sat_mock',          'SAT Mock #2 — 1320',                   '2025-05-05', 1320, 'SAT 1320',         1, TRUE,  NULL, 'Đạt target SAT!',                           'completed',  'student'),
    ('STU_001','ms_009','ielts_mock',        'IELTS Mock #3 — Overall 6.5',          '2025-06-15', 6.5,  'IELTS Band 6.5',   1, TRUE,  NULL, 'Đạt target IELTS.',                         'completed',  'student'),
    ('STU_001','ms_010','camp',              'ETEST Summer Camp — Academic Writing',  '2025-07-10', NULL, 'Trại hè',          1, TRUE,  NULL, 'Cải thiện Writing 0.5 band sau trại hè.',    'completed',  'student'),
    ('STU_001','ms_011','essay_draft',        'Supplemental Essay Draft',             '2025-09-01', NULL, 'Draft',            1, FALSE, 85, 'Essay bổ sung cho Monash.',                 'completed',  'student'),
    ('STU_001','ms_012','target_achieved',  'Đạt IELTS 6.5 + SAT 1320',            '2025-09-05', NULL, 'Milestone',        1, TRUE,  NULL, 'Hai target chính hoàn thành trước deadline.','completed','student'),

    -- ── Upcoming ─────────────────────────────────────────────────────────────
    ('STU_001','ms_013','essay_final',        'Personal Statement Final v2 (Melbourne)', '2026-04-20', NULL,'Final',      1, FALSE, NULL, NULL,                     'upcoming', 'student'),
    ('STU_001','ms_014','ielts_mock',        'IELTS Mock #4 — target 7.0',          '2026-04-30', NULL, 'IELTS Band 7.0',  1, FALSE, NULL, NULL,                     'upcoming', 'student'),
    ('STU_001','ms_015','consultation',      'Nộp hồ sơ Early Action',             '2026-05-07', NULL, 'Early Action',   1, FALSE, NULL, NULL,                     'upcoming', 'student')
ON CONFLICT (student_id, milestone_id) DO UPDATE SET
    status          = EXCLUDED.status,
    date            = EXCLUDED.date,
    mentor_approved = EXCLUDED.mentor_approved,
    auth_score      = EXCLUDED.auth_score;
```

> After this seed runs, the `trg_milestones_sync_digest` trigger automatically updates `students`:
> `progress_pct = 80` (12/15), `milestones_done = 12`, `next_deadline = 2026-04-20`, `days_left = 30`.

### 5.7 Courses — 4 sample entries (upsell catalog)

```sql
INSERT INTO courses
    (name, slug, type, program, season, description,
     target_skills, suitable_for, cta_url, cta_label,
     duration_days, start_date, end_date, location, price_vnd,
     is_featured, is_active, display_order)
VALUES
    -- ── Camp: IELTS Writing Intensive (targets Minh Anh's weakest skill) ─────
    (
        'IELTS Writing Intensive — Summer Camp 2026',
        'ielts-writing-intensive-summer-camp-2026',
        'camp',
        'IELTS',
        'Summer 2026',
        'Trại hè 2 tuần chuyên sâu IELTS Writing 6.5–7.0. Học viên được luyện tập 1:1 với mentor, chấm bài cá nhân hóa, phân tích band descriptor theo từng tiêu chí.',
        '["IELTS_Writing", "Task_Achievement", "Coherence_Cohesion", "Vocabulary"]'::jsonb,
        '["student_gap_writing", "student_target_7plus", "student_ielts_6"]'::jsonb,
        'https://etest.vn/courses/ielts-writing-summer-2026',
        'Đăng ký ngay',
        14, '2026-06-15', '2026-06-28', 'Hồ Chí Minh', 8500000,
        TRUE, TRUE, 1
    ),

    -- ── Workshop: Personal Statement Workshop (supports EA deadline) ─────────
    (
        'Personal Statement Workshop — Early Action 2026',
        'personal-statement-workshop-ea-2026',
        'workshop',
        'AMP',
        'Spring 2026',
        'Workshop 3 buổi giúp học sinh hoàn thiện Personal Statement cho Early Action. Mentor trực tiếp review outline, body paragraphs và final draft. Phù hợp với học sinh đang ở giai đoạn nộp hồ sơ.',
        '["Essay_Structure", "Personal_Statement", "Story_Telling", "Academic_Writing"]'::jsonb,
        '["student_ea_deadline", "student_amp", "student_essay_gap"]'::jsonb,
        'https://etest.vn/courses/ps-workshop-ea-2026',
        'Xem chi tiết',
        3, '2026-04-05', '2026-04-19', 'Online', 3500000,
        TRUE, TRUE, 2
    ),

    -- ── Course: SAT Math Sprint (consolidates recent SAT score) ──────────────
    (
        'SAT Math Sprint — Target 1450+',
        'sat-math-sprint-2026',
        'course',
        'SAT',
        'All Year',
        'Khóa học 6 tuần tập trung SAT Math, thiên về Problem Solving và Data Analysis — hai phần chiếm >50% điểm SAT. Phù hợp với học sinh đã đạt 1300+ muốn cải thiện lên 1450+.',
        '["SAT_Math", "Problem_Solving", "Data_Analysis", "Algebra"]'::jsonb,
        '["student_sat_1300_plus", "student_target_1450_plus"]'::jsonb,
        'https://etest.vn/courses/sat-math-sprint',
        'Đăng ký ngay',
        42, '2026-04-01', '2026-05-15', 'Online', 12000000,
        FALSE, TRUE, 3
    ),

    -- ── Camp: Speaking Booster Camp (targets speaking score) ────────────────
    (
        'IELTS Speaking Booster Camp — July 2026',
        'ielts-speaking-booster-july-2026',
        'camp',
        'IELTS',
        'Summer 2026',
        'Trại hè 1 tuần chuyên luyện IELTS Speaking Part 2 & 3. Học viên được mock test 1:1 với giáo viên bản ngữ, nhận feedback chi tiết về pronunciation, fluency và lexical resource.',
        '["IELTS_Speaking", "Pronunciation", "Fluency", "Lexical_Resource"]'::jsonb,
        '["student_gap_speaking", "student_ielts_6", "student_target_7plus"]'::jsonb,
        'https://etest.vn/courses/ielts-speaking-booster-2026',
        'Đăng ký ngay',
        7, '2026-07-01', '2026-07-07', 'Hà Nội', 5500000,
        FALSE, TRUE, 4
    )
ON CONFLICT (course_id) DO UPDATE SET
    is_active       = EXCLUDED.is_active,
    is_featured     = EXCLUDED.is_featured,
    display_order   = EXCLUDED.display_order;
```

### 5.8 Conversations — 3 items (30-day history for AI context)

```sql
INSERT INTO conversations
    (parent_id, student_id, timestamp, question, ai_response, context_snapshot, escalated, expires_at)
VALUES
    (
        1, 'STU_001',
        '2026-03-20T09:15:00+07:00',
        'Con IELTS 6.5 có đủ để vào Melbourne không?',
        'Đủ cho 8/10 trường top Australia. Riêng University of Melbourne direct entry cần 6.5 — con đã đạt! Tuy nhiên một số ngành cần 7.0. Nên tập trung cải thiện Writing lên 6.0.',
        '{"student_name":"Nguyễn Hà Minh Anh","ielts_score":6.5,"target_schools":["University of Melbourne","UNSW","Monash"],"progress_pct":68,"weakest_skill":"Writing","next_deadline":"2026-05-07"}'::jsonb,
        FALSE,
        '2026-04-19T09:15:00+07:00'
    ),
    (
        1, 'STU_001',
        '2026-02-28T20:45:00+07:00',
        'Con nên làm gì để cải thiện Writing?',
        'Minh Anh nên tập trung vào 3 điểm: (1) Task Achievement — trả lời đủ ý, (2) Coherence & Cohesion — dùng linking words tự nhiên hơn, (3) Vocabulary — tránh lặp từ. Bạn có thể đăng ký lớp Writing cuối tuần tháng 4.',
        '{"student_name":"Nguyễn Hà Minh Anh","ielts_score":6.5,"weakest_skill":"Writing","progress_pct":65}'::jsonb,
        FALSE,
        '2026-03-30T20:45:00+07:00'
    ),
    (
        1, 'STU_001',
        '2026-02-10T11:30:00+07:00',
        'Hồ sơ du học cần những gì?',
        'Hồ sơ du học Australia gồm: (1) Học bạ 3 năm, (2) IELTS/PTE, (3) Personal Statement, (4) Thư giới thiệu từ mentor, (5) Chứng chỉ hoạt động ngoại khóa.',
        '{"student_name":"Nguyễn Hà Minh Anh","program":"AMP","target_schools":["University of Melbourne","UNSW","Monash"]}'::jsonb,
        FALSE,
        '2026-03-12T11:30:00+07:00'
    );
```

> `expires_at = timestamp + 30 days`. The Feb 10 conversation (expired Mar 12) is still present in the seed — it will be cleaned up by the nightly TTL job.

---

## 6. Implementation Order (aligned H0–H3)

Aligned with the **H0–H3 Database** phase of the Tech Spec Build Order.

### H0 · Schema & Extensions (Day 0 — first 30 min)

```
Priority  Action                                              Time
────────  ───────────────────────────────────────────────     ─────
1          Install PostgreSQL 15+ locally or provision RDS     10 min
2          CREATE EXTENSION btree_gist;                        1 min
3          Init Alembic: alembic init alembic                  2 min
4          Write migration revisions (4 files)                 5 min
5          Run upgrade: alembic upgrade head                    3 min
6          Verify: SELECT * FROM pg_tables WHERE ...            2 min
```

**Alembic project structure:**

```
e-be/
├── alembic/
│   ├── alembic.ini              -- auto-generated by alembic init
│   ├── env.py                   -- PostgreSQL engine from DATABASE_URL
│   └── versions/
│       ├── 001_create_tables.py          -- CREATE TABLE all 6 tables + constraints
│       ├── 002_create_indexes.py         -- All B-tree, GIN, and partial indexes
│       ├── 003_create_triggers.py         -- Digest sync trigger function + attachment
│       └── 004_seed_demo_data.py          -- Full seed data
├── alembic.ini
└── requirements.txt             -- add: alembic, psycopg2-binary
```

#### alembic.ini

```ini
# e-be/alembic.ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql://postgres:postgres@localhost:5432/etest_one
prepend_sys_path = .
version_path_separator = os
```

#### alembic/env.py

```python
# e-be/alembic/env.py
import os
from logging.config import fileConfig
from sqlalchemy import pool, create_engine
from alembic import context

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = None   # no ORM models — raw SQL only
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:postgres@localhost:5432/etest_one'
)
connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)

def run_migrations_offline() -> None:
    """Render SQL scripts without DB connection (for CI / reviewed scripts)."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Execute against live DB."""
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

#### Example revision file (001_create_tables.py)

```python
# e-be/alembic/versions/001_create_tables.py
"""001 create tables

Revision ID: 001
Revises:
Create Date: 2026-03-21
"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Extension
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist;")

    # mentors
    op.execute("""
        CREATE TABLE mentors (
            mentor_id      SERIAL PRIMARY KEY,
            email          VARCHAR(255) NOT NULL UNIQUE,
            hashed_password VARCHAR(255) NOT NULL,
            full_name      VARCHAR(255) NOT NULL,
            programs       JSONB   DEFAULT '[]',
            max_students   SMALLINT DEFAULT 10,
            active_students SMALLINT DEFAULT 0,
            created_at     TIMESTAMPT NOT NULL DEFAULT NOW()
        );
    """)

    # parents
    op.execute("""
        CREATE TABLE parents (
            parent_id       SERIAL PRIMARY KEY,
            email           VARCHAR(255) NOT NULL UNIQUE,
            hashed_password VARCHAR(255) NOT NULL,
            full_name       VARCHAR(255) NOT NULL,
            phone           VARCHAR(20),
            student_id      VARCHAR(50) UNIQUE,  -- bidirectional 1:1 enforced here
            created_at      TIMESTAMPT NOT NULL DEFAULT NOW()
        );
    """)

    # students
    op.execute("""
        CREATE TABLE students (
            student_id       VARCHAR(50) PRIMARY KEY,
            name             VARCHAR(255) NOT NULL,
            ielts_score     DECIMAL(4,1),
            sat_score        DECIMAL(5,1),
            gpa              DECIMAL(4,2),
            skill_breakdown  JSONB,
            target_schools    JSONB,
            program          VARCHAR(100),
            months_enrolled  INTEGER DEFAULT 0,

            -- 1:1 links
            parent_id        INTEGER NOT NULL UNIQUE REFERENCES parents(parent_id) ON DELETE RESTRICT,
            mentor_id        INTEGER REFERENCES mentors(mentor_id) ON DELETE SET NULL,

            -- Trigger-maintained digest fields
            progress_pct        SMALLINT DEFAULT 0 CHECK (progress_pct BETWEEN 0 AND 100),
            milestones_done     SMALLINT DEFAULT 0,
            next_deadline      DATE,
            next_deadline_label VARCHAR(255),
            days_left          SMALLINT,
            priority_action     VARCHAR(255),

            -- Wellbeing context
            current_streak      SMALLINT DEFAULT 0,
            last_activity_date  DATE,
            upsell_cooldown     DATE DEFAULT CURRENT_DATE,

            created_at TIMESTAMPT NOT NULL DEFAULT NOW()
        );
    """)

    # courses
    op.execute("""
        CREATE TABLE courses (
            course_id       SERIAL PRIMARY KEY,
            name            VARCHAR(255) NOT NULL,
            slug            VARCHAR(255) UNIQUE,
            type            VARCHAR(50)  NOT NULL CHECK (type IN ('camp','workshop','course')),
            program         VARCHAR(100) CHECK (program IN ('AMP','IELTS','SAT','ALL')),
            season          VARCHAR(50),
            description     TEXT,
            target_skills   JSONB  DEFAULT '[]',
            suitable_for    JSONB  DEFAULT '[]',
            cta_url         VARCHAR(500),
            cta_label       VARCHAR(100),
            duration_days   SMALLINT,
            start_date      DATE,
            end_date        DATE,
            location        VARCHAR(255),
            price_vnd       BIGINT,
            is_featured     BOOLEAN DEFAULT FALSE,
            is_active       BOOLEAN DEFAULT TRUE,
            display_order   SMALLINT DEFAULT 0,
            created_at      TIMESTAMPT NOT NULL DEFAULT NOW()
        );
    """)

    # behavioral_logs
    op.execute("""
        CREATE TABLE behavioral_logs (
            id             SERIAL PRIMARY KEY,
            student_id     VARCHAR(50) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
            date           DATE         NOT NULL,
            duration_min   SMALLINT,
            session_start  TIME,
            session_end    TIME,
            studied        BOOLEAN  DEFAULT FALSE,
            streak_day     SMALLINT DEFAULT 0,
            score_delta    DECIMAL(4,1) DEFAULT 0,
            is_late_night  BOOLEAN  GENERATED ALWAYS AS (session_start >= '22:00:00') STORED,
            activities     JSONB   DEFAULT '[]',
            mood_note      TEXT,
            created_at     TIMESTAMPT NOT NULL DEFAULT NOW(),
            UNIQUE (student_id, date)
        );
    """)

    # conversations
    op.execute("""
        CREATE TABLE conversations (
            id              SERIAL PRIMARY KEY,
            parent_id       INTEGER NOT NULL REFERENCES parents(parent_id) ON DELETE CASCADE,
            student_id      VARCHAR(50) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
            timestamp       TIMESTAMPT NOT NULL DEFAULT NOW(),
            question        TEXT NOT NULL,
            ai_response     TEXT NOT NULL,
            context_snapshot JSONB,
            escalated       BOOLEAN DEFAULT FALSE,
            escalator_note  TEXT,
            expires_at      TIMESTAMPT,
            created_at      TIMESTAMPT NOT NULL DEFAULT NOW()
        );
    """)

    # milestones
    op.execute("""
        CREATE TABLE milestones (
            id                SERIAL PRIMARY KEY,
            student_id        VARCHAR(50) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
            milestone_id      VARCHAR(100) NOT NULL,
            type              VARCHAR(50) NOT NULL CHECK (type IN (
                'ielts_mock','essay_draft','essay_final','sat_mock',
                'extracurricular','consultation','camp','csr','target_achieved')),
            title             VARCHAR(255) NOT NULL,
            date              DATE NOT NULL,
            score             DECIMAL(5,2),
            score_label       VARCHAR(100),
            mentor_id         INTEGER REFERENCES mentors(mentor_id) ON DELETE SET NULL,
            mentor_approved   BOOLEAN,
            auth_score        SMALLINT CHECK (auth_score BETWEEN 0 AND 100),
            notes             TEXT,
            status            VARCHAR(20) NOT NULL DEFAULT 'upcoming'
                              CHECK (status IN ('completed','in_progress','upcoming')),
            contributor_type  VARCHAR(50) NOT NULL DEFAULT 'student'
                              CHECK (contributor_type IN ('student','mentor','parent','institution')),
            ai_summary        JSONB,
            created_at        TIMESTAMPT NOT NULL DEFAULT NOW(),
            updated_at        TIMESTAMPT NOT NULL DEFAULT NOW(),
            UNIQUE (student_id, milestone_id)
        );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS milestones CASCADE;")
    op.execute("DROP TABLE IF EXISTS conversations CASCADE;")
    op.execute("DROP TABLE IF EXISTS behavioral_logs CASCADE;")
    op.execute("DROP TABLE IF EXISTS courses CASCADE;")
    op.execute("DROP TABLE IF EXISTS students CASCADE;")
    op.execute("DROP TABLE IF EXISTS parents CASCADE;")
    op.execute("DROP TABLE IF EXISTS mentors CASCADE;")
```

### H0 Commands

```bash
cd e-be

# 1. Install dependencies
pip install alembic psycopg2-binary

# 2. Init Alembic (creates alembic/ directory + alembic.ini)
alembic init alembic

# 3. Edit alembic/env.py — paste code from above

# 4. Generate empty revision stubs
alembic revision -m "001 create tables"
alembic revision -m "002 create indexes"
alembic revision -m "003 create triggers"
alembic revision -m "004 seed demo data"

# 5. Write SQL inside each revision's upgrade() / downgrade()

# 6. Run all migrations
alembic upgrade head

# Verify
alembic current
alembic history
psql $DATABASE_URL -c "\dt"
```

### H1 · Seed Data & Connection Test (H0–H1)

Seed data lives inside `alembic/versions/004_seed_demo_data.py` and runs automatically on `alembic upgrade head`. To verify:

```bash
# Verify tables and current migration
alembic current
psql $DATABASE_URL -c "\dt"

# Quick smoke-test queries
psql $DATABASE_URL -c "SELECT s.student_id, s.name, p.full_name AS parent
    FROM students s JOIN parents p ON s.parent_id = p.parent_id;"
psql $DATABASE_URL -c "SELECT COUNT(*) FROM behavioral_logs WHERE student_id = 'STU_001';"
psql $DATABASE_URL -c "SELECT COUNT(*) FROM milestones WHERE student_id = 'STU_001' AND status = 'upcoming';"
psql $DATABASE_URL -c "SELECT COUNT(*) FROM courses WHERE is_active = TRUE;"
```
psql $DATABASE_URL -c "SELECT COUNT(*) FROM courses WHERE is_active = TRUE;"
```

### H2 · Application Connection (H1–H2)

The existing `e-be/` uses SQLAlchemy 2.0 async (`asyncpg`) via FastAPI. Verify the connection:

```python
# e-be/scripts/test_connection.py
import asyncio, json
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/etest_one"

async def test():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with AsyncSession(engine) as db:

        # Test 1: resolve parent → student
        r = await db.execute(
            text("""
                SELECT s.student_id, s.name, p.full_name AS parent_name
                FROM students s
                JOIN parents p ON s.parent_id = p.parent_id
                WHERE s.parent_id = :pid
            """).bindparams(pid=1)
        )
        row = r.one()
        print(f"✓ Student: {row.name}  (parent: {row.parent_name})")

        # Test 2: 14-day wellbeing logs
        r = await db.execute(
            text("""
                SELECT date, duration_min, is_late_night, streak_day
                FROM behavioral_logs
                WHERE student_id = 'STU_001'
                  AND date >= CURRENT_DATE - INTERVAL '14 days'
                ORDER BY date DESC
            """)
        )
        logs = r.all()
        late = [l for l in logs if l.is_late_night]
        print(f"✓ 14-day logs: {len(logs)} rows, Late nights: {len(late)}")

        # Test 3: digest card (pre-aggregated — single row)
        r = await db.execute(
            text("""
                SELECT progress_pct, milestones_done, next_deadline,
                       days_left, priority_action
                FROM students WHERE student_id = 'STU_001'
            """)
        )
        d = r.one()
        print(f"✓ Digest: {d.progress_pct}% — {d.next_deadline} ({d.days_left}d left)")

        # Test 4: active courses
        r = await db.execute(
            text("SELECT COUNT(*) FROM courses WHERE is_active = TRUE")
        )
        print(f"✓ Active courses: {r.scalar()}")

    await engine.dispose()

asyncio.run(test())
```

```bash
python -m scripts.test_connection
```

### H3 · Integration: Repository + FastAPI Routes (H2–H3, parallel with backend scaffold)

```python
# e-be/modules/smart_parenting/repository.py
import json
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


# ── Auth: resolve student from parent_id ──────────────────────────────────
async def get_student_by_parent(db: AsyncSession, parent_id: int):
    result = await db.execute(
        text("""
            SELECT s.*, p.full_name AS parent_name
            FROM students s
            JOIN parents p ON s.parent_id = p.parent_id
            WHERE s.parent_id = :pid
        """).bindparams(pid=parent_id)
    )
    return result.one_or_none()


# ── Digest card: single-row, pre-aggregated, zero computation ─────────────
async def get_digest_card(db: AsyncSession, student_id: str):
    result = await db.execute(
        text("""
            SELECT progress_pct, milestones_done, next_deadline,
                   next_deadline_label, days_left, priority_action,
                   skill_breakdown, current_streak, ielts_score, weakest_skill
            FROM students WHERE student_id = :sid
        """).bindparams(sid=student_id)
    )
    return result.one_or_none()


# ── Wellbeing: 14-day behavioral logs ─────────────────────────────────────
async def get_wellbeing_logs(db: AsyncSession, student_id: str):
    result = await db.execute(
        text("""
            SELECT date, duration_min, session_start, session_end,
                   is_late_night, streak_day, score_delta, activities
            FROM behavioral_logs
            WHERE student_id = :sid
              AND date >= CURRENT_DATE - INTERVAL '14 days'
            ORDER BY date DESC
        """).bindparams(sid=student_id)
    )
    return result.all()


# ── 30-day chat history for AI context ────────────────────────────────────
async def get_conversations(db: AsyncSession, parent_id: int):
    result = await db.execute(
        text("""
            SELECT timestamp, question, ai_response,
                   context_snapshot, escalated
            FROM conversations
            WHERE parent_id = :pid
              AND timestamp >= NOW() - INTERVAL '30 days'
            ORDER BY timestamp DESC
        """).bindparams(pid=parent_id)
    )
    return result.all()


# ── Save chat message ─────────────────────────────────────────────────────
async def save_conversation(
    db: AsyncSession,
    parent_id: int,
    student_id: str,
    question: str,
    ai_response: str,
    context_snapshot: dict,
    escalated: bool = False,
):
    await db.execute(
        text("""
            INSERT INTO conversations
              (parent_id, student_id, timestamp, question, ai_response,
               context_snapshot, escalated, expires_at)
            VALUES
              (:pid, :sid, NOW(), :q, :r, :ctx::jsonb, :esc,
               NOW() + INTERVAL '30 days')
        """).bindparams(
            pid=parent_id, sid=student_id, q=question, r=ai_response,
            ctx=json.dumps(context_snapshot), esc=escalated
        )
    )


# ── Upsell: match courses to student skill gaps ───────────────────────────
async def get_upsell_courses(db: AsyncSession, student_id: str):
    # 1. Check cooldown
    r = await db.execute(
        text("SELECT upsell_cooldown >= CURRENT_DATE FROM students WHERE student_id = :sid")
        .bindparams(sid=student_id)
    )
    if r.scalar():
        return []

    # 2. Get student profile
    r = await db.execute(
        text("SELECT skill_breakdown, program FROM students WHERE student_id = :sid")
        .bindparams(sid=student_id)
    )
    row = r.one_or_none()
    if not row:
        return []

    skills = row.skill_breakdown or {}
    weakest = sorted(skills.items(), key=lambda x: x[1])[:2]
    tags = [f"student_gap_{k.lower()}" for k, _ in weakest]

    # 3. Match courses by suitable_for JSONB overlap
    r = await db.execute(
        text("""
            SELECT course_id, name, type, season, description,
                   target_skills, cta_url, cta_label, price_vnd, location
            FROM courses
            WHERE is_active = TRUE
              AND (program IS NULL OR program = :prog)
              AND suitable_for && :tags::jsonb
            ORDER BY is_featured DESC, display_order ASC
            LIMIT 3
        """).bindparams(prog=row.program, tags=json.dumps(tags))
    )
    return r.all()


# ── Set cooldown after showing upsell ─────────────────────────────────────
async def set_upsell_cooldown(db: AsyncSession, student_id: str, days: int = 7):
    await db.execute(
        text("""
            UPDATE students
            SET upsell_cooldown = CURRENT_DATE + :d * INTERVAL '1 day'
            WHERE student_id = :sid
        """).bindparams(d=days, sid=student_id)
    )
```

---

## 7. Notes & Edge Cases

### 7.1 30-Day TTL Cleanup Job

Run via **pg_cron** (extension) every night at 03:00 UTC:

```sql
-- Enable pg_cron extension first
CREATE EXTENSION pg_cron;

-- Schedule: every day at 03:00
SELECT cron.schedule(
    'cleanup-old-conversations',
    '0 3 * * *',
    $$DELETE FROM conversations WHERE expires_at < NOW()$$
);
```

Without pg_cron, a simple cron on the host works:

```bash
# /etc/cron.d/cleanup-conversations — run at 3am daily
0 3 * * * postgres psql $DATABASE_URL -c "DELETE FROM conversations WHERE expires_at < NOW();"
```

> **Why not use `expires_at < NOW() - INTERVAL '30 days'`?** Because `expires_at` is set to `timestamp + 30 days` at insert time — it's the authoritative expiry timestamp. Using `NOW() - INTERVAL '30 days'` would be wrong for conversations created before a system clock change. Always compare against `expires_at`.

### 7.2 1:1 Parent–Student Enforcement

The `UNIQUE` constraint on `students.parent_id` + `UNIQUE` constraint on `parents.student_id` together enforce the 1:1 relationship bidirectionally. The `EXCLUDE` constraint (via `btree_gist`) on `parents.student_id` adds a DB-level guarantee independent of application logic.

If a parent tries to link a second student:

```
ERROR:  duplicate key value violates unique constraint "students_parent_id_key"
DETAIL: Key (parent_id)=(1) already exists.
```

### 7.3 `is_late_night` as Generated Column

```sql
is_late_night BOOLEAN GENERATED ALWAYS AS (session_start >= '22:00:00') STORED
```

- `STORED` means it's physically written to disk — queryable like a regular column, no function call overhead.
- Works for any `TIME` value. Sessions starting at `22:00` exactly count as late night.
- No application logic needed to compute it on read.

### 7.4 `days_left` — Trigger vs. On-Read

The trigger stores `days_left` as of the last milestone change. If tighter accuracy is needed (e.g., the card must always show the true day count including today), override at read time:

```sql
SELECT
    student_id,
    progress_pct,
    milestones_done,
    next_deadline,
    next_deadline_label,
    (next_deadline - CURRENT_DATE) AS days_left,   -- live computation
    priority_action
FROM students
WHERE student_id = 'STU_001';
```

### 7.5 Upsell Cooldown + Course Matching Logic

**Cooldown check:**

```sql
SELECT upsell_cooldown >= CURRENT_DATE AS is_cooled_down
FROM students WHERE student_id = 'STU_001';
```

**Set cooldown after showing upsell cards:**

```sql
UPDATE students
SET upsell_cooldown = CURRENT_DATE + INTERVAL '7 days'
WHERE student_id = 'STU_001';
```

**Match courses to skill gaps — Node.js logic:**

```javascript
// From student.skill_breakdown: { listening: 7.0, reading: 7.0, writing: 5.5, speaking: 6.5 }
// Weakest 2 skills → suitable_for tag pattern
const weakestTags = Object.entries(skills)
  .sort(([, a], [, b]) => a - b)   // ascending: weakest first
  .slice(0, 2)
  .map(([k]) => `student_gap_${k}`); // ["student_gap_writing", "student_gap_speaking"]

// Postgres: match courses where suitable_for overlaps with student tags
// WHERE suitable_for && $1::jsonb
// Result: IELTS Writing Intensive (target_skills includes IELTS_Writing,
//          suitable_for includes student_gap_writing)
```

### 7.6 Wellbeing 14-Day Window

Always anchor the window to `CURRENT_DATE` in the query — never hardcode dates:

```sql
SELECT date, duration_min, is_late_night, streak_day
FROM behavioral_logs
WHERE student_id = 'STU_001'
  AND date >= CURRENT_DATE - INTERVAL '14 days'
ORDER BY date DESC;
```

### 7.7 `skill_breakdown` and `target_schools` as JSONB

```javascript
// Reading from pg result
const student = await client.query(
  'SELECT skill_breakdown, target_schools FROM students WHERE student_id = $1',
  [studentId]
);
const skills = student.rows[0].skill_breakdown;     // already a JS object (pg parses JSONB)
const weakest = Object.keys(skills).reduce((a, b) =>
  skills[a] < skills[b] ? a : b                       // 'writing' — weakest skill
);

// Writing — pass JSON string
await client.query(
  'UPDATE students SET skill_breakdown = $1 WHERE student_id = $2',
  [JSON.stringify({ listening: 7.0, reading: 7.0, writing: 5.5, speaking: 6.5 }), studentId]
);
```

### 7.8 `auth_score` — Only Essays

Only `type IN ('essay_draft', 'essay_final')` milestones carry an `auth_score`. Query for authenticity scoring:

```sql
SELECT milestone_id, title, date, auth_score, ai_summary
FROM milestones
WHERE student_id = 'STU_001'
  AND type IN ('essay_draft', 'essay_final')
  AND auth_score IS NOT NULL
ORDER BY date DESC;
```

### 7.9 Upsell Engine — Module 1D Mapping

The upsell feature (Module 1D) uses three tables:

1. **`students`** → `skill_breakdown` (JSONB) identifies the student's weakest skills
2. **`courses`** → `target_skills` (JSONB) and `suitable_for` (JSONB) for matching
3. **`courses`** → `cta_url`, `cta_label`, `price_vnd`, `location` for display

**Matching algorithm (Node.js):**
1. Read `students.skill_breakdown` → find 1–2 weakest skills
2. Map weakest skill names to `suitable_for` tags (e.g. `writing` → `student_gap_writing`)
3. Query: `SELECT … FROM courses WHERE is_active = TRUE AND suitable_for && $1::jsonb`
4. Filter by student's `program` if course is program-specific
5. Show top 3 results sorted by `is_featured` DESC, `display_order` ASC
6. Set `upsell_cooldown = CURRENT_DATE + 7 days` after display

### 7.10 Backend Route Summary — PostgreSQL + Node.js/pg Equivalent

| Route | DynamoDB Operation | PostgreSQL Equivalent | Node.js/pg |
|---|---|---|---|
| `GET /api/students/:id` | `GetItem Students[PK=studentId]` | `SELECT * FROM students WHERE student_id = :id` | `client.query('SELECT … FROM students WHERE student_id = $1', [id])` |
| `GET /api/digest/:id` | 3 × `Query` + JS compute | `SELECT progress_pct, milestones_done, next_deadline, days_left, priority_action FROM students WHERE student_id = :id` — single row, no joins | `getDigestCard(studentId, client)` |
| `GET /api/behavioral-log/:id` | `Query BehavioralLogs[PK=studentId, SK range]` | `SELECT * FROM behavioral_logs WHERE student_id = :id AND date >= CURRENT_DATE - 14 days ORDER BY date DESC` | `getWellbeingLogs(studentId, client)` |
| `POST /api/ai/parent-chat` | `GetItem` + `PutItem` | `SELECT student` + `INSERT INTO conversations` | `getConversations(parentId, client)` → after response, `INSERT INTO conversations` |
| `POST /api/ai/wellbeing` | `Query` 14 days | Same `SELECT … WHERE date >= CURRENT_DATE - 14 days` | `getWellbeingLogs(studentId, client)` — then Node.js computes severity |
| `GET /api/upsell/:id` | `GetItem Students` + scan courses | `SELECT skill_breakdown FROM students` + cooldown check + `SELECT … FROM courses WHERE suitable_for && $1` | `getUpsellCourses(studentId, client)` |
| `POST /api/behavioral-log` | `PutItem` | `INSERT … ON CONFLICT DO UPDATE` + `UPDATE students SET current_streak` | `upsertBehavioralLog(studentId, data, client)` |

### 7.11 Docker Compose for Local Dev

```yaml
# e-be/docker-compose.yml  (add to existing setup)
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: etest_one
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  pgdata:
```

```bash
# Start PostgreSQL
docker compose up postgres -d

# Run migrations
psql $DATABASE_URL -f e-be/db/migrations/V001__create_tables.sql
psql $DATABASE_URL -f e-be/db/migrations/V002__create_indexes.sql
psql $DATABASE_URL -f e-be/db/migrations/V003__create_triggers.sql

# Seed demo data
psql $DATABASE_URL -f e-be/db/migrations/V004__seed_demo_data.sql
```

### 7.12 Table Dependency Order (for migrations and seeding)

Tables must be created and seeded in this order due to `REFERENCES` foreign keys:

```
1. parents        — no dependencies
2. mentors        — no dependencies
3. students       — FK: parents(parent_id), mentors(mentor_id)
4. courses        — no dependencies (standalone catalog)
5. behavioral_logs — FK: students(student_id)
6. conversations  — FK: parents(parent_id), students(student_id)
7. milestones     — FK: students(student_id), mentors(mentor_id)

Seed order:
1. mentors
2. parents
3. students
4. courses
5. behavioral_logs
6. milestones      → fires trigger → updates students digest columns
7. conversations
```
