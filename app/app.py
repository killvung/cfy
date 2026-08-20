"""Gradio review UI for Phase 0 cat image feedback."""

from __future__ import annotations

import gradio as gr

from app.db import SupabaseReviewStore, get_review_store
from app.render import ReviewRenderer
from app.styles import APP_TITLE, CUSTOM_CSS
from app.ui.controller import ReviewController
from app.ui.layout import ReviewUI
from app.ui.wiring import wire_review_events


def create_app(store: SupabaseReviewStore | None = None) -> gr.Blocks:
    review_store = store or get_review_store()
    controller = ReviewController(review_store, ReviewRenderer(review_store))

    with gr.Blocks(title=APP_TITLE) as demo:
        ui = ReviewUI.build()
        wire_review_events(demo, ui, controller)
        _wire_zerogpu_probe()

    return demo


def _wire_zerogpu_probe() -> None:
    """Hidden handler required when the Space runs on ZeroGPU hardware."""
    from app.zerogpu import startup_probe

    probe = gr.Button("", visible=False)
    probe.click(fn=startup_probe, inputs=None, outputs=None, show_progress="hidden")


def main() -> None:
    create_app().launch(css=CUSTOM_CSS, theme=gr.themes.Soft())


if __name__ == "__main__":
    main()
