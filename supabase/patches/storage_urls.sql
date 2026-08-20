-- Set HF bucket resolve URLs for Phase 0 static cat images.
-- Bucket: killvung/cat-feedback-assets (public)
-- Safe to re-run: overwrites storage_url for matching local_path rows.

UPDATE images
SET storage_url = 'https://huggingface.co/buckets/killvung/cat-feedback-assets/resolve/'
    || regexp_replace(local_path, '^data/static/cat_a/', '')
WHERE local_path ~ '^data/static/cat_a/[0-9]{2}\.jpg$';
