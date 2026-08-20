# Phase 0 data model

Entity-relationship diagram for the Supabase schema in [`migrations/20260819200000_init.sql`](migrations/20260819200000_init.sql).

## ER diagram

```mermaid
erDiagram
    cats ||--o{ images : has
    cats ||--o{ evaluation_tasks : has
    invites ||--|| sessions : "one per link"
    evaluation_tasks ||--|{ task_candidates : contains
    images ||--o{ task_candidates : "shown as"
    sessions ||--o{ feedback : submits
    evaluation_tasks ||--o{ feedback : "for task"
    images ||--o{ feedback : "rates"

    cats {
        uuid id PK
        text slug UK
        text display_name
        timestamptz created_at
    }

    invites {
        uuid id PK
        text token UK
        text evaluator_label
        boolean is_active
        timestamptz created_at
    }

    sessions {
        uuid id PK
        uuid invite_id FK
        timestamptz created_at
    }

    images {
        uuid id PK
        uuid cat_id FK
        text local_path
        text storage_url
        text prompt
        text negative_prompt
        text base_model
        text lora_version
        bigint seed
        jsonb generation_settings
        text batch_id
        timestamptz created_at
    }

    evaluation_tasks {
        uuid id PK
        uuid cat_id FK
        text test_id
        text batch_id
        timestamptz created_at
    }

    task_candidates {
        uuid task_id PK
        uuid image_id PK
        smallint slot UK
    }

    feedback {
        uuid id PK
        uuid session_id FK
        uuid task_id FK
        uuid image_id FK
        smallint accepted
        timestamptz submitted_at
    }
```

Note: `sessions.invite_id`, `cats.slug`, and `invites.token` are UNIQUE in SQL; Mermaid allows only one of `PK` / `FK` / `UK` per attribute line, so those uniques are documented here and in the relationships table.

## Relationships

| From | To | Cardinality | Notes |
| --- | --- | --- | --- |
| `cats` | `images` | 1:N | Each image belongs to one cat |
| `cats` | `evaluation_tasks` | 1:N | Each task evaluates one cat |
| `invites` | `sessions` | 1:1 | One session per invite link (`invite_id` UNIQUE) |
| `evaluation_tasks` | `task_candidates` | 1:4 | Up to four slots per task |
| `images` | `task_candidates` | 1:N | Same image can appear in multiple tasks later |
| `sessions` + `evaluation_tasks` + `images` | `feedback` | N:1 each | UNIQUE `(session_id, task_id, image_id)` |

## Review flow

```text
invite (private link)
  → session (1 per invite)
    → feedback (4 rows per submit: accepted 0/1)
      ← tied to evaluation_task + image

evaluation_task
  → task_candidates (slot 1–4)
    → images (with generation provenance)
      ← cat
```

Feedback is append-only: each submission writes one row per candidate image. Resubmit for the same session and task is blocked by the unique constraint.
