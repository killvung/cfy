"""Resolve candidate image paths for display in the review UI."""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

from app.config import PROJECT_ROOT

_BUCKET_MOUNT = os.environ.get("IMAGE_BUCKET_MOUNT", "/data").rstrip("/")
_BUCKET_BASE = os.environ.get(
    "IMAGE_BUCKET_BASE",
    "https://huggingface.co/buckets/killvung/cat-feedback-assets/resolve",
).rstrip("/")


def _resolve_storage_url(storage_url: str) -> str | None:
    url = storage_url.strip()
    if not url:
        return None
    parsed = urlparse(url)
    if parsed.scheme in ("http", "https") and parsed.netloc:
        return url
    if _BUCKET_BASE:
        return f"{_BUCKET_BASE}/{url.lstrip('/')}"
    return None


def _resolve_local_path(local_path: str) -> str | None:
    path = Path(local_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    if path.is_file():
        return str(path)

    if _BUCKET_MOUNT:
        # Bucket sync puts files at root: data/static/cat_a/01.jpg -> /data/01.jpg
        filename = Path(local_path).name
        mounted = Path(_BUCKET_MOUNT) / filename
        if mounted.is_file():
            return str(mounted)

    return None


def image_display_value(
    local_path: str | None,
    storage_url: str | None = None,
) -> str | None:
    """Return a URL or filesystem path gr.Image can render, or None if missing."""
    if storage_url:
        resolved = _resolve_storage_url(storage_url)
        if resolved:
            return resolved

    if local_path:
        return _resolve_local_path(local_path)

    return None
