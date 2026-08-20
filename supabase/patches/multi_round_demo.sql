-- Adds rounds 2–3 and images 05–12 for existing Phase 0 databases that only have one task.
-- Safe to re-run: uses fixed UUIDs and ON CONFLICT DO NOTHING.

INSERT INTO images (id, cat_id, local_path, storage_url, prompt, negative_prompt, base_model, lora_version, seed, generation_settings, batch_id) VALUES
    ('d5555555-5555-5555-5555-555555555555', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'data/static/cat_a/05.jpg', 'https://huggingface.co/buckets/killvung/cat-feedback-assets/resolve/05.jpg', 'a photo of Cat A playing with a toy', 'blurry, low quality', 'static', 'none', 1005, '{"steps": 0, "guidance_scale": 0}', 'static-batch-002'),
    ('d6666666-6666-6666-6666-666666666666', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'data/static/cat_a/06.jpg', 'https://huggingface.co/buckets/killvung/cat-feedback-assets/resolve/06.jpg', 'a photo of Cat A playing with a toy', 'blurry, low quality', 'static', 'none', 1006, '{"steps": 0, "guidance_scale": 0}', 'static-batch-002'),
    ('d7777777-7777-7777-7777-777777777777', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'data/static/cat_a/07.jpg', 'https://huggingface.co/buckets/killvung/cat-feedback-assets/resolve/07.jpg', 'a photo of Cat A playing with a toy', 'blurry, low quality', 'static', 'none', 1007, '{"steps": 0, "guidance_scale": 0}', 'static-batch-002'),
    ('d8888888-8888-8888-8888-888888888888', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'data/static/cat_a/08.jpg', 'https://huggingface.co/buckets/killvung/cat-feedback-assets/resolve/08.jpg', 'a photo of Cat A playing with a toy', 'blurry, low quality', 'static', 'none', 1008, '{"steps": 0, "guidance_scale": 0}', 'static-batch-002'),
    ('d9999999-9999-9999-9999-999999999999', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'data/static/cat_a/09.jpg', 'https://huggingface.co/buckets/killvung/cat-feedback-assets/resolve/09.jpg', 'a photo of Cat A napping on a couch', 'blurry, low quality', 'static', 'none', 1009, '{"steps": 0, "guidance_scale": 0}', 'static-batch-003'),
    ('daaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'data/static/cat_a/10.jpg', 'https://huggingface.co/buckets/killvung/cat-feedback-assets/resolve/10.jpg', 'a photo of Cat A napping on a couch', 'blurry, low quality', 'static', 'none', 1010, '{"steps": 0, "guidance_scale": 0}', 'static-batch-003'),
    ('dbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'data/static/cat_a/11.jpg', 'https://huggingface.co/buckets/killvung/cat-feedback-assets/resolve/11.jpg', 'a photo of Cat A napping on a couch', 'blurry, low quality', 'static', 'none', 1011, '{"steps": 0, "guidance_scale": 0}', 'static-batch-003'),
    ('dccccccc-cccc-cccc-cccc-cccccccccccc', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'data/static/cat_a/12.jpg', 'https://huggingface.co/buckets/killvung/cat-feedback-assets/resolve/12.jpg', 'a photo of Cat A napping on a couch', 'blurry, low quality', 'static', 'none', 1012, '{"steps": 0, "guidance_scale": 0}', 'static-batch-003')
ON CONFLICT (id) DO NOTHING;

INSERT INTO evaluation_tasks (id, cat_id, test_id, batch_id) VALUES
    ('e2222222-2222-2222-2222-222222222222', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'phase0-round-002', 'static-batch-002'),
    ('e3333333-3333-3333-3333-333333333333', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'phase0-round-003', 'static-batch-003')
ON CONFLICT (id) DO NOTHING;

-- Rename legacy single-round task id for consistency (no-op if already renamed).
UPDATE evaluation_tasks
SET test_id = 'phase0-round-001', batch_id = 'static-batch-001'
WHERE id = 'e1111111-1111-1111-1111-111111111111'
  AND test_id = 'phase0-test-001';

INSERT INTO task_candidates (task_id, image_id, slot) VALUES
    ('e2222222-2222-2222-2222-222222222222', 'd5555555-5555-5555-5555-555555555555', 1),
    ('e2222222-2222-2222-2222-222222222222', 'd6666666-6666-6666-6666-666666666666', 2),
    ('e2222222-2222-2222-2222-222222222222', 'd7777777-7777-7777-7777-777777777777', 3),
    ('e2222222-2222-2222-2222-222222222222', 'd8888888-8888-8888-8888-888888888888', 4),
    ('e3333333-3333-3333-3333-333333333333', 'd9999999-9999-9999-9999-999999999999', 1),
    ('e3333333-3333-3333-3333-333333333333', 'daaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 2),
    ('e3333333-3333-3333-3333-333333333333', 'dbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 3),
    ('e3333333-3333-3333-3333-333333333333', 'dccccccc-cccc-cccc-cccc-cccccccccccc', 4)
ON CONFLICT (task_id, image_id) DO NOTHING;
