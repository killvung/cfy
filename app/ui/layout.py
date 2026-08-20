"""Review UI component tree (Gradio Blocks layout)."""

from __future__ import annotations

from dataclasses import dataclass, field

import gradio as gr

from app.render import CANDIDATE_COUNT, OUTPUT_KEYS
from app.styles import (
    ACCEPTED_COUNT_INITIAL,
    APP_TITLE,
    BTN_ALL_DONE,
    BTN_CONTINUE,
    BTN_GO_BACK,
    BTN_PREVIOUS,
    BTN_SELECT,
    CAT_SUBTEXT,
    COMPLETE_HEADING,
    PRIMARY_INSTRUCTION,
)


def _candidate_image() -> gr.Image:
    return gr.Image(
        interactive=False,
        show_label=False,
        container=False,
        buttons=[],
        elem_classes=["candidate-photo"],
    )


def _build_card_row(
    slots: tuple[int, ...],
) -> tuple[list[gr.Image], list[gr.Column], list[gr.Button]]:
    images: list[gr.Image] = []
    cards: list[gr.Column] = []
    select_buttons: list[gr.Button] = []

    with gr.Row(elem_classes=["grid-row"]):
        for slot in slots:
            with gr.Column(elem_classes=["card-col"]) as card_col:
                cards.append(card_col)
                gr.Markdown(f"**Candidate {slot}**", elem_classes=["candidate-label"])
                images.append(_candidate_image())
                select_buttons.append(
                    gr.Button(BTN_SELECT, elem_classes=["select-btn", "select-btn-off"])
                )

    return images, cards, select_buttons


@dataclass
class ReviewUI:
    """Registry of all Gradio components for the review app."""

    ctx: gr.State
    task: gr.State
    selections: gr.State
    error_panel: gr.Markdown
    review_screen: gr.Column
    complete_screen: gr.Column
    cat_heading: gr.Markdown
    progress: gr.Markdown
    images: list[gr.Image] = field(default_factory=list)
    cards: list[gr.Column] = field(default_factory=list)
    select_buttons: list[gr.Button] = field(default_factory=list)
    accepted_count: gr.Markdown | None = None
    status_message: gr.Markdown | None = None
    primary_btn: gr.Button | None = None
    prev_btn: gr.Button | None = None
    all_done_nav_btn: gr.Button | None = None
    all_done_extra_btn: gr.Button | None = None
    go_back_btn: gr.Button | None = None
    _components: dict[str, gr.components.Component] = field(default_factory=dict, repr=False)

    @property
    def state_inputs(self) -> list[gr.State]:
        return [self.ctx, self.task, self.selections]

    @property
    def outputs(self) -> list[gr.components.Component]:
        return [self._components[key] for key in OUTPUT_KEYS]

    @classmethod
    def build(cls) -> ReviewUI:
        ctx_state = gr.State(None)
        task_state = gr.State(None)
        selections_state = gr.State([False] * CANDIDATE_COUNT)

        gr.Markdown(f"# {APP_TITLE}", elem_classes=["review-header"])
        gr.Markdown(PRIMARY_INSTRUCTION, elem_classes=["review-header"])

        error_panel = gr.Markdown("", elem_classes=["error-banner"], visible=False)

        with gr.Column(visible=False) as review_screen:
            with gr.Column(elem_classes=["review-body"]):
                with gr.Column(elem_classes=["cat-block"]):
                    cat_heading = gr.Markdown("")
                    gr.Markdown(CAT_SUBTEXT)
                progress = gr.Markdown("")

                row1_images, row1_cards, row1_buttons = _build_card_row((1, 2))
                row2_images, row2_cards, row2_buttons = _build_card_row((3, 4))
                images = row1_images + row2_images
                cards = row1_cards + row2_cards
                select_buttons = row1_buttons + row2_buttons

                accepted_count = gr.Markdown(
                    ACCEPTED_COUNT_INITIAL, elem_classes=["accepted-count"]
                )
                status_message = gr.Markdown("", elem_classes=["status-message"])

                with gr.Row(elem_classes=["actions-row"]):
                    prev_btn = gr.Button(
                        BTN_PREVIOUS, elem_classes=["secondary-btn"], visible=False
                    )
                    primary_btn = gr.Button(BTN_CONTINUE, elem_classes=["primary-btn"])
                    all_done_nav_btn = gr.Button(
                        BTN_ALL_DONE, elem_classes=["secondary-btn"], visible=False
                    )

                all_done_extra_btn = gr.Button(
                    BTN_ALL_DONE, elem_classes=["all-done-row"], visible=False
                )

        with gr.Column(visible=False) as complete_screen:
            gr.Markdown(COMPLETE_HEADING, elem_classes=["complete-box"])
            with gr.Row(elem_classes=["complete-actions"]):
                go_back_btn = gr.Button(BTN_GO_BACK, elem_classes=["secondary-btn"])

        components = {
            "ctx": ctx_state,
            "task": task_state,
            "selections": selections_state,
            "error_panel": error_panel,
            "review_screen": review_screen,
            "complete_screen": complete_screen,
            "cat_heading": cat_heading,
            "progress": progress,
            **{f"image_{index}": images[index] for index in range(CANDIDATE_COUNT)},
            **{f"card_{index}": cards[index] for index in range(CANDIDATE_COUNT)},
            **{f"select_{index}": select_buttons[index] for index in range(CANDIDATE_COUNT)},
            "accepted_count": accepted_count,
            "status_message": status_message,
            "primary_btn": primary_btn,
            "prev_btn": prev_btn,
            "all_done_nav_btn": all_done_nav_btn,
            "all_done_extra_btn": all_done_extra_btn,
        }

        return cls(
            ctx=ctx_state,
            task=task_state,
            selections=selections_state,
            error_panel=error_panel,
            review_screen=review_screen,
            complete_screen=complete_screen,
            cat_heading=cat_heading,
            progress=progress,
            images=images,
            cards=cards,
            select_buttons=select_buttons,
            accepted_count=accepted_count,
            status_message=status_message,
            primary_btn=primary_btn,
            prev_btn=prev_btn,
            all_done_nav_btn=all_done_nav_btn,
            all_done_extra_btn=all_done_extra_btn,
            go_back_btn=go_back_btn,
            _components=components,
        )
