"""Apply schema migrations and seed to a hosted Supabase project.

Secret keys (`sb_secret_...`) authenticate the Data API (Streamlit / analytics).
They cannot run DDL. Schema changes use the Management API with a personal
access token (`sbp_...`), which is the current programmatic equivalent of
`supabase db push`.

Docs:
  https://supabase.com/docs/guides/deployment/database-migrations
  https://supabase.com/docs/reference/api/v1-apply-a-migration
  https://supabase.com/docs/guides/getting-started/api-keys
"""

from __future__ import annotations

import sys
from pathlib import Path

import httpx

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.config import (
    get_supabase_access_token,
    get_supabase_project_ref,
)

# / acts as a shortcut to join file paths together cleanly.
# In this case: PROJECT_ROOT/supabase/migrations
MIGRATIONS_DIR = PROJECT_ROOT / "supabase" / "migrations"

SEED_PATH = PROJECT_ROOT / "supabase" / "seed.sql"
MULTI_ROUND_PATCH_PATH = PROJECT_ROOT / "supabase" / "patches" / "multi_round_demo.sql"
MANAGEMENT_API = "https://api.supabase.com/v1"


def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def _migration_name(path: Path) -> str:
    return path.stem


def list_applied(client: httpx.Client, ref: str) -> set[str]:
    response = client.get(f"{MANAGEMENT_API}/projects/{ref}/database/migrations")
    response.raise_for_status()
    payload = response.json()
    applied: set[str] = set()
    if isinstance(payload, list):
        for row in payload:
            if isinstance(row, dict):
                if row.get("version") is not None:
                    applied.add(str(row["version"]))
                if row.get("name") is not None:
                    applied.add(str(row["name"]))
    return applied


def is_migration_applied(applied: set[str], path: Path) -> bool:
    name = _migration_name(path)
    if name in applied:
        return True
    # Management API may record a server-assigned version distinct from the filename prefix.
    timestamp_prefix = name.split("_", 1)[0]
    return timestamp_prefix in applied


def apply_migration(client: httpx.Client, ref: str, path: Path) -> None:
    query = path.read_text(encoding="utf-8")
    name = _migration_name(path)
    response = client.post(
        f"{MANAGEMENT_API}/projects/{ref}/database/migrations",
        json={"query": query, "name": name},
    )
    if not response.is_success:
        raise RuntimeError(
            f"Migration {name} failed ({response.status_code}): {response.text}"
        )
    print(f"Applied migration {name}")


def apply_seed(client: httpx.Client, ref: str) -> None:
    check = client.post(
        f"{MANAGEMENT_API}/projects/{ref}/database/query",
        json={"query": "select 1 from invites limit 1"},
    )
    if check.is_success and check.json():
        print("Skipping seed (invites already present)")
    else:
        query = SEED_PATH.read_text(encoding="utf-8")
        response = client.post(
            f"{MANAGEMENT_API}/projects/{ref}/database/query",
            json={"query": query},
        )
        if not response.is_success:
            raise RuntimeError(f"Seed failed ({response.status_code}): {response.text}")
        print("Applied supabase/seed.sql")

    apply_multi_round_patch(client, ref)


def apply_multi_round_patch(client: httpx.Client, ref: str) -> None:
    check = client.post(
        f"{MANAGEMENT_API}/projects/{ref}/database/query",
        json={"query": "select count(*)::int as n from evaluation_tasks"},
    )
    check.raise_for_status()
    rows = check.json()
    task_count = rows[0]["n"] if rows else 0
    if task_count >= 3:
        print("Skipping multi-round patch (already has 3+ tasks)")
        return

    query = MULTI_ROUND_PATCH_PATH.read_text(encoding="utf-8")
    response = client.post(
        f"{MANAGEMENT_API}/projects/{ref}/database/query",
        json={"query": query},
    )
    if not response.is_success:
        raise RuntimeError(
            f"Multi-round patch failed ({response.status_code}): {response.text}"
        )
    print("Applied supabase/patches/multi_round_demo.sql")


def main() -> None:
    token = get_supabase_access_token()
    ref = get_supabase_project_ref()
    files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not files:
        raise RuntimeError(f"No SQL files in {MIGRATIONS_DIR}")

    with httpx.Client(headers=_headers(token), timeout=180.0) as client:
        applied = list_applied(client, ref)
        for path in files:
            name = _migration_name(path)
            if is_migration_applied(applied, path):
                print(f"Skipping already-applied {name}")
                continue
            apply_migration(client, ref, path)
        apply_seed(client, ref)


if __name__ == "__main__":
    main()
