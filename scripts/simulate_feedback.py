"""Simulate reviewer feedback for end-to-end validation."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db import get_review_store  # noqa: E402

DEMO_TOKENS = [
    "invite-reviewer-1-a7b3c9d2",
    "invite-reviewer-2-e4f8a1b6",
    "invite-reviewer-3-c2d5f7a9",
]

# Deterministic acceptance pattern per reviewer (slot 1-based)
PATTERNS = {
    DEMO_TOKENS[0]: [True, True, False, False],
    DEMO_TOKENS[1]: [True, False, True, False],
    DEMO_TOKENS[2]: [False, True, True, True],
}


def simulate_reviewer(token: str) -> int:
    store = get_review_store()
    invite = store.get_invite_by_token(token)
    if invite is None:
        raise RuntimeError(f"Invalid invite token: {token}")

    session_id = store.get_or_create_session(invite.id)
    tasks = store.list_all_evaluation_tasks()
    pattern = PATTERNS[token]
    rows = 0

    for task in tasks:
        selections = {
            candidate.id: pattern[candidate.slot - 1]
            for candidate in task.candidates
        }
        store.submit_feedback(session_id, task.id, selections)
        rows += len(selections)

    print(f"{invite.evaluator_label.value}: submitted {rows} feedback rows across {len(tasks)} tasks")
    return rows


def main() -> int:
    total = 0
    for token in DEMO_TOKENS:
        total += simulate_reviewer(token)
    print(f"Total feedback rows: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
