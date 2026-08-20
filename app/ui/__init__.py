"""Gradio UI layer: layout, controller, event wiring."""

from app.ui.controller import ReviewController
from app.ui.layout import ReviewUI
from app.ui.wiring import wire_review_events

__all__ = ["ReviewController", "ReviewUI", "wire_review_events"]
