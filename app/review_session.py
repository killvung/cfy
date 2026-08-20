"""Review session orchestration for the Gradio UI."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.db import SupabaseReviewStore
from app.exceptions import DuplicateFeedbackError
from app.models import EvaluationTask, Invite

# Phase 0 reviewer UI only loads seed tasks (3 × 4 images).
PHASE0_TEST_PREFIX = "phase0-"


def _review_tasks(store: SupabaseReviewStore) -> list[EvaluationTask]:
    return [
        task
        for task in store.list_all_evaluation_tasks()
        if task.test_id.startswith(PHASE0_TEST_PREFIX)
    ]


def _next_unsubmitted_task(
    store: SupabaseReviewStore,
    session_id: str,
    tasks: list[EvaluationTask],
) -> EvaluationTask | None:
    for task in tasks:
        if not store.has_feedback_for_session_task(session_id, task.id):
            return task
    return None


@dataclass
class ReviewContext:
    invite_token: str = ""
    evaluator_label: str = ""
    session_id: str = ""
    task_ids: list[str] = field(default_factory=list)
    completed_task_ids: set[str] = field(default_factory=set)
    current_index: int = 0
    screen: str = "error"  # error | review | complete
    error_message: str = ""
    status_message: str = ""


def _selections_for_task(
    store: SupabaseReviewStore,
    session_id: str,
    task: EvaluationTask,
) -> list[bool]:
    accepted = store.get_accepted_image_ids(session_id, task.id)
    return [candidate.id in accepted for candidate in task.candidates]


def _task_by_index(store: SupabaseReviewStore, task_ids: list[str], index: int) -> EvaluationTask | None:
    if index < 0 or index >= len(task_ids):
        return None
    return store.get_evaluation_task(task_ids[index])


def bootstrap_review(
    store: SupabaseReviewStore,
    invite_token: str | None,
) -> tuple[ReviewContext, EvaluationTask | None, list[bool]]:
    ctx = ReviewContext()

    token = (invite_token or "").strip()
    if not token:
        ctx.screen = "error"
        ctx.error_message = "Missing invite link. Open the private URL shared with you."
        return ctx, None, [False, False, False, False]

    try:
        invite = store.get_invite_by_token(token)
    except Exception as exc:
        ctx.screen = "error"
        ctx.error_message = f"Could not connect to the review backend: {exc}"
        return ctx, None, [False, False, False, False]

    if invite is None:
        ctx.screen = "error"
        ctx.error_message = "This invite link is invalid or inactive."
        return ctx, None, [False, False, False, False]

    ctx.invite_token = token
    ctx.evaluator_label = invite.evaluator_label.value
    ctx.session_id = store.get_or_create_session(invite.id)
    ctx.completed_task_ids = store.get_completed_task_ids(ctx.session_id)

    tasks = _review_tasks(store)
    if not tasks:
        ctx.screen = "error"
        ctx.error_message = "No evaluation tasks are configured yet."
        return ctx, None, [False, False, False, False]

    ctx.task_ids = [task.id for task in tasks]
    total = len(ctx.task_ids)

    if _next_unsubmitted_task(store, ctx.session_id, tasks) is None:
        ctx.screen = "complete"
        ctx.current_index = total - 1
        task = _task_by_index(store, ctx.task_ids, ctx.current_index)
        selections = _selections_for_task(store, ctx.session_id, task) if task else [False] * 4
        return ctx, task, selections

    next_task = _next_unsubmitted_task(store, ctx.session_id, tasks)
    assert next_task is not None
    ctx.screen = "review"
    ctx.current_index = ctx.task_ids.index(next_task.id)
    selections = _selections_for_task(store, ctx.session_id, next_task)
    return ctx, next_task, selections


def load_task_at_index(
    store: SupabaseReviewStore,
    ctx: ReviewContext,
    index: int,
    *,
    screen: str = "review",
) -> tuple[ReviewContext, EvaluationTask | None, list[bool]]:
    ctx = ReviewContext(
        invite_token=ctx.invite_token,
        evaluator_label=ctx.evaluator_label,
        session_id=ctx.session_id,
        task_ids=list(ctx.task_ids),
        completed_task_ids=set(ctx.completed_task_ids),
        current_index=index,
        screen=screen,
    )
    task = _task_by_index(store, ctx.task_ids, index)
    if task is None:
        ctx.screen = "error"
        ctx.error_message = "No evaluation tasks are configured yet."
        return ctx, None, [False, False, False, False]
    selections = _selections_for_task(store, ctx.session_id, task)
    return ctx, task, selections


def save_current_task(
    store: SupabaseReviewStore,
    ctx: ReviewContext,
    task: EvaluationTask,
    selections: list[bool],
) -> ReviewContext:
    if len(selections) != len(task.candidates):
        raise ValueError("Selection count does not match candidate count")

    payload = {
        candidate.id: bool(selected)
        for candidate, selected in zip(task.candidates, selections, strict=True)
    }
    try:
        store.submit_feedback(ctx.session_id, task.id, payload)
    except DuplicateFeedbackError:
        ctx.status_message = "These images were already saved."
        ctx.completed_task_ids.add(task.id)
        return ctx
    except Exception as exc:
        ctx.status_message = f"Could not save feedback: {exc}"
        return ctx

    ctx.status_message = ""
    ctx.completed_task_ids.add(task.id)
    return ctx


def continue_from_current(
    store: SupabaseReviewStore,
    ctx: ReviewContext,
    task: EvaluationTask,
    selections: list[bool],
) -> tuple[ReviewContext, EvaluationTask | None, list[bool]]:
    ctx = save_current_task(store, ctx, task, selections)
    if ctx.status_message:
        return ctx, task, selections

    next_index = ctx.current_index + 1
    while next_index < len(ctx.task_ids):
        candidate_id = ctx.task_ids[next_index]
        if not store.has_feedback_for_session_task(ctx.session_id, candidate_id):
            return load_task_at_index(store, ctx, next_index)
        next_index += 1

    ctx.screen = "complete"
    ctx.current_index = len(ctx.task_ids) - 1
    last_task = _task_by_index(store, ctx.task_ids, ctx.current_index)
    last_selections = (
        _selections_for_task(store, ctx.session_id, last_task) if last_task else [False] * 4
    )
    return ctx, last_task, last_selections


def save_and_advance(
    store: SupabaseReviewStore,
    ctx: ReviewContext,
    task: EvaluationTask,
    selections: list[bool],
) -> tuple[ReviewContext, EvaluationTask | None, list[bool]]:
    ctx = save_current_task(store, ctx, task, selections)
    if ctx.status_message:
        return ctx, task, selections

    next_index = ctx.current_index + 1
    if next_index < len(ctx.task_ids):
        return load_task_at_index(store, ctx, next_index)

    ctx.screen = "complete"
    ctx.current_index = len(ctx.task_ids) - 1
    last_task = _task_by_index(store, ctx.task_ids, ctx.current_index)
    last_selections = (
        _selections_for_task(store, ctx.session_id, last_task) if last_task else [False] * 4
    )
    return ctx, last_task, last_selections


def go_previous(
    store: SupabaseReviewStore,
    ctx: ReviewContext,
) -> tuple[ReviewContext, EvaluationTask | None, list[bool]]:
    if ctx.current_index <= 0:
        return load_task_at_index(store, ctx, 0)
    return load_task_at_index(store, ctx, ctx.current_index - 1)


def go_complete(
    store: SupabaseReviewStore,
    ctx: ReviewContext,
) -> tuple[ReviewContext, EvaluationTask | None, list[bool]]:
    if not ctx.task_ids:
        ctx.screen = "error"
        ctx.error_message = "No evaluation tasks are configured yet."
        return ctx, None, [False, False, False, False]
    ctx.screen = "complete"
    index = len(ctx.task_ids) - 1
    ctx.current_index = index
    task = _task_by_index(store, ctx.task_ids, index)
    selections = _selections_for_task(store, ctx.session_id, task) if task else [False] * 4
    return ctx, task, selections


def go_back_from_complete(
    store: SupabaseReviewStore,
    ctx: ReviewContext,
) -> tuple[ReviewContext, EvaluationTask | None, list[bool]]:
    return load_task_at_index(store, ctx, len(ctx.task_ids) - 1)


def all_tasks_submitted(store: SupabaseReviewStore, ctx: ReviewContext) -> bool:
    if not ctx.task_ids:
        return False
    return all(task_id in ctx.completed_task_ids for task_id in ctx.task_ids)


def task_was_saved(store: SupabaseReviewStore, ctx: ReviewContext, task: EvaluationTask) -> bool:
    return store.has_feedback_for_session_task(ctx.session_id, task.id)
