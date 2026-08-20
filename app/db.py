"""Supabase-backed review store."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from supabase import Client

from app.enums import CatSlug, EvaluatorLabel
from app.exceptions import DuplicateFeedbackError, DuplicateSessionError
from app.models import CandidateImage, EvaluationTask, Invite


def _is_unique_violation(exc: Exception) -> bool:
    message = str(exc).lower()
    return "duplicate key" in message or "23505" in message


class SupabaseReviewStore:
    def __init__(self, client: Client) -> None:
        self._client = client

    def get_invite_by_token(self, token: str) -> Invite | None:
        response = (
            self._client.table("invites")
            .select("id, token, evaluator_label, is_active")
            .eq("token", token)
            .limit(1)
            .execute()
        )
        rows = response.data or []
        if not rows:
            return None
        row = rows[0]
        if not row.get("is_active"):
            return None
        return Invite(
            id=row["id"],
            token=row["token"],
            evaluator_label=EvaluatorLabel(row["evaluator_label"]),
            is_active=row["is_active"],
        )

    def get_or_create_session(self, invite_id: str) -> str:
        response = (
            self._client.table("sessions")
            .select("id")
            .eq("invite_id", invite_id)
            .limit(1)
            .execute()
        )
        rows = response.data or []
        if rows:
            return rows[0]["id"]

        session_id = str(uuid4())
        try:
            self._client.table("sessions").insert(
                {"id": session_id, "invite_id": invite_id}
            ).execute()
        except Exception as exc:
            if not _is_unique_violation(exc):
                raise
            response = (
                self._client.table("sessions")
                .select("id")
                .eq("invite_id", invite_id)
                .limit(1)
                .execute()
            )
            rows = response.data or []
            if not rows:
                raise DuplicateSessionError from exc
            return rows[0]["id"]
        return session_id

    def _completed_task_ids(self, session_id: str) -> set[str]:
        response = (
            self._client.table("feedback")
            .select("task_id")
            .eq("session_id", session_id)
            .execute()
        )
        return {row["task_id"] for row in (response.data or []) if row.get("task_id")}

    def get_completed_task_ids(self, session_id: str) -> set[str]:
        return self._completed_task_ids(session_id)

    def _build_evaluation_task(self, task_row: dict[str, Any]) -> EvaluationTask:
        cat = task_row.get("cats") or {}
        candidate_response = (
            self._client.table("task_candidates")
            .select(
                "slot, images(id, local_path, storage_url, prompt, base_model, lora_version, seed)"
            )
            .eq("task_id", task_row["id"])
            .order("slot")
            .execute()
        )
        candidate_rows = candidate_response.data or []

        candidates: list[CandidateImage] = []
        for row in candidate_rows:
            image = row.get("images") or {}
            image_id = image.get("id")
            if image_id is None:
                continue
            candidates.append(
                CandidateImage(
                    id=image_id,
                    slot=row["slot"],
                    local_path=image.get("local_path") or "",
                    storage_url=image.get("storage_url"),
                    prompt=image.get("prompt"),
                    base_model=image.get("base_model"),
                    lora_version=image.get("lora_version"),
                    seed=image.get("seed"),
                )
            )

        cat_slug_raw = cat.get("slug") or ""
        return EvaluationTask(
            id=task_row["id"],
            test_id=task_row["test_id"],
            batch_id=task_row["batch_id"],
            cat_slug=CatSlug(cat_slug_raw),
            cat_display_name=cat.get("display_name", ""),
            candidates=candidates,
        )

    def _list_task_rows(self) -> list[dict[str, Any]]:
        response = (
            self._client.table("evaluation_tasks")
            .select("id, test_id, batch_id, cat_id, cats(slug, display_name)")
            .order("created_at")
            .execute()
        )
        return response.data or []

    def count_evaluation_tasks(self) -> int:
        response = (
            self._client.table("evaluation_tasks")
            .select("id", count="exact")
            .execute()
        )
        return response.count or 0

    def count_completed_tasks(self, session_id: str) -> int:
        return len(self._completed_task_ids(session_id))

    def get_next_evaluation_task(self, session_id: str) -> EvaluationTask | None:
        completed = self._completed_task_ids(session_id)
        for task_row in self._list_task_rows():
            if task_row["id"] not in completed:
                return self._build_evaluation_task(task_row)
        return None

    def get_evaluation_task(self, task_id: str) -> EvaluationTask | None:
        response = (
            self._client.table("evaluation_tasks")
            .select("id, test_id, batch_id, cat_id, cats(slug, display_name)")
            .eq("id", task_id)
            .limit(1)
            .execute()
        )
        rows = response.data or []
        if not rows:
            return None
        return self._build_evaluation_task(rows[0])

    def list_all_evaluation_tasks(self) -> list[EvaluationTask]:
        return [self._build_evaluation_task(row) for row in self._list_task_rows()]

    def list_completed_tasks(self, session_id: str) -> list[EvaluationTask]:
        completed = self._completed_task_ids(session_id)
        tasks: list[EvaluationTask] = []
        for task_row in self._list_task_rows():
            if task_row["id"] in completed:
                tasks.append(self._build_evaluation_task(task_row))
        return tasks

    def get_task_round_number(self, task_id: str) -> int:
        for index, task_row in enumerate(self._list_task_rows(), start=1):
            if task_row["id"] == task_id:
                return index
        return 1

    def get_accepted_image_ids(self, session_id: str, task_id: str) -> set[str]:
        response = (
            self._client.table("feedback")
            .select("image_id, accepted")
            .eq("session_id", session_id)
            .eq("task_id", task_id)
            .execute()
        )
        return {
            row["image_id"]
            for row in (response.data or [])
            if row.get("accepted") == 1 and row.get("image_id")
        }

    def get_first_evaluation_task(self) -> EvaluationTask | None:
        rows = self._list_task_rows()
        if not rows:
            return None
        return self._build_evaluation_task(rows[0])

    def has_feedback_for_session_task(self, session_id: str, task_id: str) -> bool:
        response = (
            self._client.table("feedback")
            .select("id")
            .eq("session_id", session_id)
            .eq("task_id", task_id)
            .limit(1)
            .execute()
        )
        return bool(response.data)

    def submit_feedback(
        self,
        session_id: str,
        task_id: str,
        selections: dict[str, bool],
    ) -> None:
        rows: list[dict[str, Any]] = []
        for image_id, accepted in selections.items():
            rows.append(
                {
                    "session_id": session_id,
                    "task_id": task_id,
                    "image_id": image_id,
                    "accepted": 1 if accepted else 0,
                }
            )
        try:
            self._client.table("feedback").upsert(
                rows,
                on_conflict="session_id,task_id,image_id",
            ).execute()
        except Exception as exc:
            if _is_unique_violation(exc):
                raise DuplicateFeedbackError from exc
            raise


def get_review_store() -> SupabaseReviewStore:
    from app.config import create_supabase_client

    return SupabaseReviewStore(create_supabase_client())
