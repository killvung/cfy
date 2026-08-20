"""Map review session state to Gradio component updates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import gradio as gr

from app.db import SupabaseReviewStore
from app.images import image_display_value
from app.models import EvaluationTask
from app.review_session import ReviewContext, all_tasks_submitted

CANDIDATE_COUNT = 4

OUTPUT_KEYS: tuple[str, ...] = (
    "ctx",
    "task",
    "selections",
    "error_panel",
    "review_screen",
    "complete_screen",
    "cat_heading",
    "progress",
    *(f"image_{index}" for index in range(CANDIDATE_COUNT)),
    *(f"card_{index}" for index in range(CANDIDATE_COUNT)),
    *(f"select_{index}" for index in range(CANDIDATE_COUNT)),
    "accepted_count",
    "status_message",
    "primary_btn",
    "prev_btn",
    "all_done_nav_btn",
    "all_done_extra_btn",
)


@dataclass
class ReviewRenderer:
    store: SupabaseReviewStore

    @staticmethod
    def toggle_selection(selections: list[bool], index: int) -> list[bool]:
        updated = list(selections)
        updated[index] = not updated[index]
        return updated

    def progress_md(self, ctx: ReviewContext) -> str:
        if not ctx.task_ids:
            return ""
        parts: list[str] = []
        for index, task_id in enumerate(ctx.task_ids):
            if task_id in ctx.completed_task_ids:
                parts.append('<span class="done">●</span>')
            elif index == ctx.current_index:
                parts.append('<span class="here">◉</span>')
            else:
                parts.append("○")
        return f'<p class="progress">{"".join(parts)}</p>'

    def _card_update(self, selected: bool) -> gr.Update:
        return gr.update(elem_classes=["card-col", "selected"] if selected else ["card-col"])

    def _select_update(self, selected: bool) -> gr.Update:
        return gr.update(
            value="✓ Selected" if selected else "Select",
            elem_classes=["select-btn", "select-btn-on" if selected else "select-btn-off"],
        )

    def build_toggle_updates(
        self,
        index: int,
        ctx: ReviewContext,
        selections: list[bool],
    ) -> dict[str, Any]:
        """Minimal updates for Select toggle — no images, no DB, no full re-render."""
        ctx.status_message = ""
        updates: dict[str, Any] = {
            "ctx": ctx,
            "selections": selections,
            "status_message": gr.update(value="", elem_classes=["status-message"]),
            "accepted_count": gr.update(
                value=f"Accepted so far — **{sum(selections)} / 4**"
            ),
            f"card_{index}": self._card_update(selections[index]),
            f"select_{index}": self._select_update(selections[index]),
        }
        return updates

    def render_toggle(
        self,
        index: int,
        ctx: ReviewContext,
        selections: list[bool],
    ) -> tuple:
        return self.pack(self.build_toggle_updates(index, ctx, selections))

    def _empty_candidates(self, updates: dict[str, Any]) -> None:
        for index in range(CANDIDATE_COUNT):
            updates[f"image_{index}"] = gr.update(value=None)
            updates[f"card_{index}"] = gr.update(elem_classes=["card-col"])
            updates[f"select_{index}"] = gr.update(
                value="Select", elem_classes=["select-btn", "select-btn-off"]
            )

    def _candidate_updates(
        self,
        updates: dict[str, Any],
        task: EvaluationTask,
        selections: list[bool],
    ) -> None:
        for index, candidate in enumerate(task.candidates):
            display = image_display_value(candidate.local_path)
            selected = selections[index] if index < len(selections) else False
            if display is None:
                updates[f"image_{index}"] = gr.update(
                    value=None, label=f"Missing image: {candidate.local_path or 'unknown'}"
                )
            else:
                updates[f"image_{index}"] = gr.update(value=display, label=None)
            updates[f"card_{index}"] = self._card_update(selected)
            updates[f"select_{index}"] = self._select_update(selected)

    def _status_update(self, ctx: ReviewContext) -> gr.Update:
        classes = ["status-message"]
        if ctx.status_message.startswith(("Could not", "These")):
            classes.append("status-error")
        elif ctx.status_message:
            classes.append("status-ok")
        return gr.update(value=ctx.status_message, elem_classes=classes)

    def build_updates(
        self,
        ctx: ReviewContext,
        task: EvaluationTask | None,
        selections: list[bool],
    ) -> dict[str, Any]:
        updates: dict[str, Any] = {"ctx": ctx, "task": task, "selections": selections}

        if ctx.screen == "error":
            updates.update(
                {
                    "error_panel": gr.update(value=ctx.error_message, visible=True),
                    "review_screen": gr.update(visible=False),
                    "complete_screen": gr.update(visible=False),
                }
            )
            return updates

        updates["error_panel"] = gr.update(value="", visible=False)

        if ctx.screen == "complete":
            updates.update(
                {
                    "review_screen": gr.update(visible=False),
                    "complete_screen": gr.update(visible=True),
                }
            )
            return updates

        updates["complete_screen"] = gr.update(visible=False)
        updates["review_screen"] = gr.update(visible=True)

        if task is None:
            updates["cat_heading"] = gr.update(value="")
            updates["progress"] = gr.update(value="")
            updates["accepted_count"] = gr.update(value="Accepted so far — **0 / 4**")
            updates["status_message"] = gr.update(value="")
            self._empty_candidates(updates)
            updates["primary_btn"] = gr.update(value="Continue")
            updates["prev_btn"] = gr.update(visible=False)
            updates["all_done_nav_btn"] = gr.update(visible=False)
            updates["all_done_extra_btn"] = gr.update(visible=False)
            return updates

        self._candidate_updates(updates, task, selections)

        accepted = sum(selections)
        all_done = all_tasks_submitted(self.store, ctx)
        on_first = ctx.current_index == 0
        on_last = ctx.current_index >= len(ctx.task_ids) - 1

        updates["cat_heading"] = gr.update(value=f"### {task.cat_display_name}")
        updates["progress"] = gr.update(value=self.progress_md(ctx))
        updates["accepted_count"] = gr.update(value=f"Accepted so far — **{accepted} / 4**")
        updates["primary_btn"] = gr.update(value="Finish" if on_last else "Continue")
        updates["prev_btn"] = gr.update(visible=not on_first)
        updates["all_done_nav_btn"] = gr.update(visible=on_first and all_done)
        updates["all_done_extra_btn"] = gr.update(visible=(not on_first) and all_done)
        updates["status_message"] = self._status_update(ctx)
        return updates

    def pack(self, updates: dict[str, Any]) -> tuple:
        return tuple(updates.get(key, gr.update()) for key in OUTPUT_KEYS)

    def render(
        self,
        ctx: ReviewContext,
        task: EvaluationTask | None,
        selections: list[bool],
    ) -> tuple:
        return self.pack(self.build_updates(ctx, task, selections))
