"""Event handlers: session actions → render updates."""

from __future__ import annotations

import gradio as gr

from app.db import SupabaseReviewStore
from app.models import EvaluationTask
from app.render import ReviewRenderer
from app.review_session import (
    ReviewContext,
    bootstrap_review,
    go_back_from_complete,
    go_complete,
    go_previous,
    save_and_advance,
)


class ReviewController:
    """Maps Gradio events to review session logic and UI updates."""

    def __init__(self, store: SupabaseReviewStore, renderer: ReviewRenderer) -> None:
        self._store = store
        self._renderer = renderer

    def render(
        self,
        ctx: ReviewContext,
        task: EvaluationTask | None,
        selections: list[bool],
    ) -> tuple:
        return self._renderer.render(ctx, task, selections)

    def on_load(
        self,
        request: gr.Request,
        ctx: ReviewContext | None,
        task: EvaluationTask | None,
        selections: list[bool],
    ) -> tuple:
        ctx, task, selections = bootstrap_review(
            self._store, request.query_params.get("invite", "")
        )
        return self.render(ctx, task, selections)

    def on_toggle(
        self,
        index: int,
        ctx: ReviewContext | None,
        task: EvaluationTask | None,
        selections: list[bool],
    ) -> tuple:
        if task is None or ctx is None:
            return self.render(ctx, task, selections)
        selections = self._renderer.toggle_selection(selections, index)
        return self._renderer.render_toggle(index, ctx, selections)

    def on_primary(
        self,
        ctx: ReviewContext | None,
        task: EvaluationTask | None,
        selections: list[bool],
    ) -> tuple:
        if task is None or ctx is None:
            return self.render(ctx, task, selections)
        ctx, task, selections = save_and_advance(self._store, ctx, task, selections)
        return self.render(ctx, task, selections)

    def on_previous(
        self,
        ctx: ReviewContext | None,
        task: EvaluationTask | None,
        selections: list[bool],
    ) -> tuple:
        if ctx is None:
            return self.render(ctx, task, selections)
        return self.render(*go_previous(self._store, ctx))

    def on_complete(
        self,
        ctx: ReviewContext | None,
        task: EvaluationTask | None,
        selections: list[bool],
    ) -> tuple:
        if ctx is None:
            return self.render(ctx, task, selections)
        return self.render(*go_complete(self._store, ctx))

    def on_back_from_complete(
        self,
        ctx: ReviewContext | None,
        task: EvaluationTask | None,
        selections: list[bool],
    ) -> tuple:
        if ctx is None:
            return self.render(ctx, task, selections)
        return self.render(*go_back_from_complete(self._store, ctx))
