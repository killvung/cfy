"""Validate evaluation task / candidate seed integrity."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import get_client  # noqa: E402


def main() -> int:
    client = get_client()

    tasks = (
        client.table("evaluation_tasks")
        .select("id, test_id, batch_id")
        .order("created_at")
        .execute()
        .data
        or []
    )
    if not tasks:
        print("FAIL: no evaluation_tasks rows")
        return 1

    errors: list[str] = []
    for task in tasks:
        task_id = task["id"]
        candidates = (
            client.table("task_candidates")
            .select("slot, image_id")
            .eq("task_id", task_id)
            .order("slot")
            .execute()
            .data
            or []
        )
        if len(candidates) != 4:
            errors.append(f"{task['test_id']}: expected 4 candidates, got {len(candidates)}")
            continue
        slots = [row["slot"] for row in candidates]
        if slots != [1, 2, 3, 4]:
            errors.append(f"{task['test_id']}: invalid slots {slots}")

    if errors:
        print("FAIL:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"OK: {len(tasks)} tasks × 4 candidates validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
