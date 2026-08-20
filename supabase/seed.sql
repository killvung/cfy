-- Phase 0 seed: one cat, twelve images, three rounds (4 images each), three invite tokens
-- Run after init migration

-- Cats (placeholders until real names are provided)
INSERT INTO cats (id, slug, display_name) VALUES
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'cat_a', 'Cat A'),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'cat_b', 'Cat B'),
    ('cccccccc-cccc-cccc-cccc-cccccccccccc', 'cat_c', 'Cat C');

-- Private invite tokens for three reviewers
INSERT INTO invites (id, token, evaluator_label, is_active) VALUES
    ('11111111-1111-1111-1111-111111111111', 'invite-reviewer-1-a7b3c9d2', 'reviewer_1', true),
    ('22222222-2222-2222-2222-222222222222', 'invite-reviewer-2-e4f8a1b6', 'reviewer_2', true),
    ('33333333-3333-3333-3333-333333333333', 'invite-reviewer-3-c2d5f7a9', 'reviewer_3', true);

-- Twelve static placeholder images for Cat A (3 rounds × 4 candidates)
-- storage_url: public HF bucket (killvung/cat-feedback-assets)
INSERT INTO images (id, cat_id, local_path, storage_url, prompt, negative_prompt, base_model, lora_version, seed, generation_settings, batch_id) VALUES
    ('d1111111-1111-1111-1111-111111111111', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'data/static/cat_a/01.jpg', 'https://huggingface.co/buckets/killvung/cat-feedback-assets/resolve/01.jpg', 'a photo of Cat A sitting on a windowsill', 'blurry, low quality', 'static', 'none', 1001, '{"steps": 0, "guidance_scale": 0}', 'static-batch-001'),
    ('d2222222-2222-2222-2222-222222222222', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'data/static/cat_a/02.jpg', 'https://huggingface.co/buckets/killvung/cat-feedback-assets/resolve/02.jpg', 'a photo of Cat A sitting on a windowsill', 'blurry, low quality', 'static', 'none', 1002, '{"steps": 0, "guidance_scale": 0}', 'static-batch-001'),
    ('d3333333-3333-3333-3333-333333333333', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'data/static/cat_a/03.jpg', 'https://huggingface.co/buckets/killvung/cat-feedback-assets/resolve/03.jpg', 'a photo of Cat A sitting on a windowsill', 'blurry, low quality', 'static', 'none', 1003, '{"steps": 0, "guidance_scale": 0}', 'static-batch-001'),
    ('d4444444-4444-4444-4444-444444444444', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'data/static/cat_a/04.jpg', 'https://huggingface.co/buckets/killvung/cat-feedback-assets/resolve/04.jpg', 'a photo of Cat A sitting on a windowsill', 'blurry, low quality', 'static', 'none', 1004, '{"steps": 0, "guidance_scale": 0}', 'static-batch-001'),
    ('d5555555-5555-5555-5555-555555555555', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'data/static/cat_a/05.jpg', 'https://huggingface.co/buckets/killvung/cat-feedback-assets/resolve/05.jpg', 'a photo of Cat A playing with a toy', 'blurry, low quality', 'static', 'none', 1005, '{"steps": 0, "guidance_scale": 0}', 'static-batch-002'),
    ('d6666666-6666-6666-6666-666666666666', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'data/static/cat_a/06.jpg', 'https://huggingface.co/buckets/killvung/cat-feedback-assets/resolve/06.jpg', 'a photo of Cat A playing with a toy', 'blurry, low quality', 'static', 'none', 1006, '{"steps": 0, "guidance_scale": 0}', 'static-batch-002'),
    ('d7777777-7777-7777-7777-777777777777', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'data/static/cat_a/07.jpg', 'https://huggingface.co/buckets/killvung/cat-feedback-assets/resolve/07.jpg', 'a photo of Cat A playing with a toy', 'blurry, low quality', 'static', 'none', 1007, '{"steps": 0, "guidance_scale": 0}', 'static-batch-002'),
    ('d8888888-8888-8888-8888-888888888888', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'data/static/cat_a/08.jpg', 'https://huggingface.co/buckets/killvung/cat-feedback-assets/resolve/08.jpg', 'a photo of Cat A playing with a toy', 'blurry, low quality', 'static', 'none', 1008, '{"steps": 0, "guidance_scale": 0}', 'static-batch-002'),
    ('d9999999-9999-9999-9999-999999999999', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'data/static/cat_a/09.jpg', 'https://huggingface.co/buckets/killvung/cat-feedback-assets/resolve/09.jpg', 'a photo of Cat A napping on a couch', 'blurry, low quality', 'static', 'none', 1009, '{"steps": 0, "guidance_scale": 0}', 'static-batch-003'),
    ('daaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'data/static/cat_a/10.jpg', 'https://huggingface.co/buckets/killvung/cat-feedback-assets/resolve/10.jpg', 'a photo of Cat A napping on a couch', 'blurry, low quality', 'static', 'none', 1010, '{"steps": 0, "guidance_scale": 0}', 'static-batch-003'),
    ('dbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'data/static/cat_a/11.jpg', 'https://huggingface.co/buckets/killvung/cat-feedback-assets/resolve/11.jpg', 'a photo of Cat A napping on a couch', 'blurry, low quality', 'static', 'none', 1011, '{"steps": 0, "guidance_scale": 0}', 'static-batch-003'),
    ('dccccccc-cccc-cccc-cccc-cccccccccccc', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'data/static/cat_a/12.jpg', 'https://huggingface.co/buckets/killvung/cat-feedback-assets/resolve/12.jpg', 'a photo of Cat A napping on a couch', 'blurry, low quality', 'static', 'none', 1012, '{"steps": 0, "guidance_scale": 0}', 'static-batch-003');

-- Three evaluation rounds (shown sequentially per session)
INSERT INTO evaluation_tasks (id, cat_id, test_id, batch_id) VALUES
    ('e1111111-1111-1111-1111-111111111111', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'phase0-round-001', 'static-batch-001'),
    ('e2222222-2222-2222-2222-222222222222', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'phase0-round-002', 'static-batch-002'),
    ('e3333333-3333-3333-3333-333333333333', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'phase0-round-003', 'static-batch-003');

INSERT INTO task_candidates (task_id, image_id, slot) VALUES
    ('e1111111-1111-1111-1111-111111111111', 'd1111111-1111-1111-1111-111111111111', 1),
    ('e1111111-1111-1111-1111-111111111111', 'd2222222-2222-2222-2222-222222222222', 2),
    ('e1111111-1111-1111-1111-111111111111', 'd3333333-3333-3333-3333-333333333333', 3),
    ('e1111111-1111-1111-1111-111111111111', 'd4444444-4444-4444-4444-444444444444', 4),
    ('e2222222-2222-2222-2222-222222222222', 'd5555555-5555-5555-5555-555555555555', 1),
    ('e2222222-2222-2222-2222-222222222222', 'd6666666-6666-6666-6666-666666666666', 2),
    ('e2222222-2222-2222-2222-222222222222', 'd7777777-7777-7777-7777-777777777777', 3),
    ('e2222222-2222-2222-2222-222222222222', 'd8888888-8888-8888-8888-888888888888', 4),
    ('e3333333-3333-3333-3333-333333333333', 'd9999999-9999-9999-9999-999999999999', 1),
    ('e3333333-3333-3333-3333-333333333333', 'daaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 2),
    ('e3333333-3333-3333-3333-333333333333', 'dbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 3),
    ('e3333333-3333-3333-3333-333333333333', 'dccccccc-cccc-cccc-cccc-cccccccccccc', 4);
