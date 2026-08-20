-- Phase 0 schema: cats, invites, sessions, images, tasks, append-only feedback

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Cats
CREATE TABLE cats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- stable id for code/config (e.g. cat_a);
    slug TEXT NOT NULL UNIQUE,  
    -- display_name is human-readable (e.g. Cat A)
    display_name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Private invite links for evaluators
CREATE TABLE invites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    token TEXT NOT NULL UNIQUE,
    -- anonymous reviewer label for analytics (e.g. reviewer_1); not a login account
    evaluator_label TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Anonymous browser sessions tied to an invite (one session per invite link)
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invite_id UUID NOT NULL UNIQUE REFERENCES invites(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Generated / static candidate images with full provenance
CREATE TABLE images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cat_id UUID NOT NULL REFERENCES cats(id) ON DELETE CASCADE,
    local_path TEXT,
    storage_url TEXT,
    prompt TEXT,
    negative_prompt TEXT,
    base_model TEXT,
    lora_version TEXT,
    seed BIGINT,
    generation_settings JSONB,
    batch_id TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_images_cat_id ON images(cat_id);
CREATE INDEX idx_images_batch_id ON images(batch_id);

-- One evaluation task (e.g. one test with four candidates)
CREATE TABLE evaluation_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cat_id UUID NOT NULL REFERENCES cats(id) ON DELETE CASCADE,
    test_id TEXT NOT NULL,
    batch_id TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_evaluation_tasks_cat_id ON evaluation_tasks(cat_id);

-- Four candidates per task, ordered by slot
CREATE TABLE task_candidates (
    task_id UUID NOT NULL REFERENCES evaluation_tasks(id) ON DELETE CASCADE,
    image_id UUID NOT NULL REFERENCES images(id) ON DELETE CASCADE,
    slot SMALLINT NOT NULL CHECK (slot >= 1 AND slot <= 4),
    PRIMARY KEY (task_id, image_id),
    UNIQUE (task_id, slot)
);

-- Append-only feedback: one row per image shown per session
CREATE TABLE feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    task_id UUID NOT NULL REFERENCES evaluation_tasks(id) ON DELETE CASCADE,
    image_id UUID NOT NULL REFERENCES images(id) ON DELETE CASCADE,
    accepted SMALLINT NOT NULL CHECK (accepted IN (0, 1)),
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (session_id, task_id, image_id)
);

CREATE INDEX idx_feedback_session_id ON feedback(session_id);
CREATE INDEX idx_feedback_task_id ON feedback(task_id);
CREATE INDEX idx_feedback_image_id ON feedback(image_id);
