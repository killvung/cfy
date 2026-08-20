"""Resolve candidate image paths for display in the review UI."""

from __future__ import annotations

from pathlib import Path

from app.config import PROJECT_ROOT


def image_display_value(local_path: str | None) -> str | None:
    """Return a filesystem path gr.Image can render, or None if missing."""
    if not local_path:
        return None
    path = Path(local_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    if path.is_file():
        return str(path)
    return None
