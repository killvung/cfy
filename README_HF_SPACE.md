---
title: Cat Image Review
emoji: 🐱
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 5.12.0
app_file: app.py
pinned: false
license: mit
---

# Cat Image Review

Private invite-link review UI for cat image feedback (Phase 0).

## Space secrets

Set these in **Settings → Repository secrets** (Space secrets):

| Secret | Description |
| --- | --- |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_SECRET_KEY` | Supabase secret key (`sb_secret_...`) |

Optional for Phase 1+ bucket access:

| Secret | Description |
| --- | --- |
| `HF_TOKEN` | Hugging Face token with bucket read/write access |

## Image assets

Phase 0 candidate images are served from the public HF bucket
[`killvung/cat-feedback-assets`](https://huggingface.co/buckets/killvung/cat-feedback-assets).
Supabase `images.storage_url` points at bucket resolve URLs; the app prefers those over
local `data/static/` paths (local dev still uses files on disk).

The bucket is also mounted at `/data` on the Space for future read/write (Phase 1+).

## Usage

Open the Space with a private invite token:

```text
?invite=invite-reviewer-1-a7b3c9d2
```

Reviewers select acceptable images across batches of four candidates. Feedback is stored in Supabase.

## Local development

```bash
pip install -r requirements.txt
cp .env.example .env  # add Supabase credentials
python app.py
```

Then open `http://127.0.0.1:7860/?invite=invite-reviewer-1-a7b3c9d2`.
