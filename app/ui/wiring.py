"""Bind Gradio event listeners to the review controller."""

from __future__ import annotations

import gradio as gr

from app.ui.controller import ReviewController
from app.ui.layout import ReviewUI


def wire_review_events(
    demo: gr.Blocks,
    ui: ReviewUI,
    controller: ReviewController,
) -> None:
    """Attach load/click handlers (unidirectional: state in → updates out)."""
    inputs = ui.state_inputs
    outputs = ui.outputs

    demo.load(controller.on_load, inputs=inputs, outputs=outputs)

    for index, button in enumerate(ui.select_buttons):
        button.click(
            fn=lambda ctx, task, sel, i=index: controller.on_toggle(i, ctx, task, sel),
            inputs=inputs,
            outputs=outputs,
            show_progress="hidden",
        )

    ui.primary_btn.click(controller.on_primary, inputs=inputs, outputs=outputs)
    ui.prev_btn.click(controller.on_previous, inputs=inputs, outputs=outputs)
    ui.all_done_nav_btn.click(controller.on_complete, inputs=inputs, outputs=outputs)
    ui.all_done_extra_btn.click(controller.on_complete, inputs=inputs, outputs=outputs)
    ui.go_back_btn.click(controller.on_back_from_complete, inputs=inputs, outputs=outputs)
