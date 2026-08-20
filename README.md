---
title: Cat Image Review
emoji: 🐱
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: "6.25.0"
app_file: app.py
pinned: false
license: mit
short_description: Private invite-link cat image review (Phase 0)
---

# Cat Image Feedback Fine-Tuning

Feedback-driven system for generating and evaluating images of specific cats. Phase 0 is a static evaluation prototype: no training or generation.

## Phase 0 scope

- Private invite links for three reviewers
- Three pages of four static candidate images each (twelve images total)
- Multi-select feedback stored in Supabase
- Batch analytics report computing acceptance rate

## Setup

### 1. Supabase project and secret key

1. Create a new project at [supabase.com](https://supabase.com)
2. Open **Settings > API Keys**, click **Create new API Keys** if needed, and copy:
   - Project URL → `SUPABASE_URL`
   - **Secret key** (`sb_secret_...`) → `SUPABASE_SECRET_KEY`  
     Use this on the backend only. It replaces the legacy `service_role` JWT (deprecated by the end of 2026). Do not put it in `Authorization: Bearer`; the Python client sends it as `apikey`.

Secret keys authenticate the Data API (review backend and analytics). They **cannot** apply schema DDL.

### 2. Apply schema (Management API or CLI)

**Recommended programmatic path** — Management API with a [personal access token](https://supabase.com/dashboard/account/tokens) (`sbp_...`):

```bash
# add SUPABASE_ACCESS_TOKEN=sbp_... to .env
python scripts/migrate_remote.py
```

That script calls `POST /v1/projects/{ref}/database/migrations` for each file in `supabase/migrations/`, then runs `supabase/seed.sql` via `POST /v1/projects/{ref}/database/query`.

**CLI equivalent:**

```bash
supabase login
supabase link --project-ref <your-project-ref>
supabase db push --include-seed
```

`supabase db push` uses your CLI login (or `SUPABASE_ACCESS_TOKEN`) plus the database password. It is not authenticated with `sb_secret_...`.

### 3. Local environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with SUPABASE_URL and SUPABASE_SECRET_KEY
```

### 4. Review UI (Gradio)

```bash
python app.py
```

Open with a demo invite token:

```text
http://127.0.0.1:7860/?invite=invite-reviewer-1-a7b3c9d2
```

Reviewer UX is specified in [`docs/review-ui-ux.md`](docs/review-ui-ux.md). Backend access lives in `app/db.py` (`SupabaseReviewStore`, `get_review_store()`).

**Hugging Face Space:** see [`README_HF_SPACE.md`](README_HF_SPACE.md). Set Space secrets `SUPABASE_URL` and `SUPABASE_SECRET_KEY`. Entry point is root [`app.py`](app.py).

Demo invite tokens (wire into your frontend as `?invite=…`):

```
invite-reviewer-1-a7b3c9d2
invite-reviewer-2-e4f8a1b6
invite-reviewer-3-c2d5f7a9
```

### 5. Run analytics

```bash
python analytics/report.py
```

Prints acceptance-rate tables and saves charts under `analytics/output/`.

## Project layout

| Directory | Purpose |
| --- | --- |
| `app/` | Supabase review store, Gradio UI (`app/app.py`), models, config |
| `app.py` | Hugging Face Space / local Gradio entrypoint |
| `analytics/` | Feedback queries and acceptance-rate reports |
| `supabase/` | SQL migration, seed data, and [data model diagram](docs/data-model.md) |
| `data/static/` | Static candidate images for Phase 0 |
| `training/`, `generation/`, `evaluation/` | Placeholders for later phases |
| `scripts/` | Migration and validation helpers |

## Primary metric

```
acceptance rate = accepted images / images shown
```

## Guiding principles

- Feedback is collected in batches; clicking never updates a model.
- Raw feedback is append-only; metrics are derived in analytics.
- Every image row carries provenance metadata for later version comparisons.
