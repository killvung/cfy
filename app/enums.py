"""Stable identifiers shared with seed data and analytics."""

from __future__ import annotations

from enum import StrEnum


class CatSlug(StrEnum):
    CAT_A = "cat_a"
    CAT_B = "cat_b"
    CAT_C = "cat_c"


class EvaluatorLabel(StrEnum):
    REVIEWER_1 = "reviewer_1"
    REVIEWER_2 = "reviewer_2"
    REVIEWER_3 = "reviewer_3"
