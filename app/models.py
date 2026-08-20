"""Domain models for the Phase 0 review app."""

from __future__ import annotations

from dataclasses import dataclass

from app.enums import CatSlug, EvaluatorLabel


@dataclass(frozen=True, slots=True)
class Invite:
    id: str
    token: str
    evaluator_label: EvaluatorLabel
    is_active: bool


@dataclass(frozen=True, slots=True)
class CandidateImage:
    id: str
    slot: int
    local_path: str
    storage_url: str | None
    prompt: str | None
    base_model: str | None
    lora_version: str | None
    seed: int | None


@dataclass(frozen=True, slots=True)
class EvaluationTask:
    id: str
    test_id: str
    batch_id: str
    cat_slug: CatSlug
    cat_display_name: str
    candidates: list[CandidateImage]
