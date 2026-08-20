"""Review UI copy and CSS."""

APP_TITLE = "Cat Image Review"
PRIMARY_INSTRUCTION = (
    "Tap **Select** on every image you consider acceptable, then continue."
)
CAT_SUBTEXT = "Pick any number of images (including none)."

BTN_SELECT = "Select"
BTN_CONTINUE = "Continue"
BTN_PREVIOUS = "Previous images"
BTN_ALL_DONE = "All done"
BTN_GO_BACK = "Go back to previous images"
COMPLETE_HEADING = "## All done. Thank you!"
ACCEPTED_COUNT_INITIAL = "Accepted so far — **0 / 4**"

# Gradio 6: gr.Image reserves empty space when height= is set. Omit height and
# collapse the preview container so the card hugs the image (see gradio #9080).
CUSTOM_CSS = """
.gradio-container {
    max-width: 1000px !important; margin: 0 auto !important;
    padding: 1.25rem 1rem 2rem !important;
}
.review-header { text-align: center; margin-bottom: 0.25rem !important; }
.review-header p { margin: 0.35rem 0 !important; color: #4b5563; }
.error-banner {
    background: #fef2f2; border: 1px solid #fecaca; border-radius: 10px;
    padding: 1rem; color: #991b1b; text-align: center;
}
.review-body { max-width: 920px; margin: 0 auto; }
.cat-block { text-align: center; margin-bottom: 0.5rem !important; }
.cat-block h3 { margin: 0.25rem 0 !important; font-size: 1.5rem !important; }
.cat-block p { margin: 0.15rem 0 0.75rem !important; color: #6b7280 !important; font-size: 0.95rem !important; }
.progress { text-align: center; letter-spacing: 0.4em; color: #9ca3af; margin: 0 0 1.25rem; font-size: 1rem; }
.progress .done { color: #22c55e; }
.progress .here { color: #2563eb; }
.grid-row { gap: 1rem !important; align-items: start !important; }
.card-col {
    border: 3px solid #e5e7eb !important; border-radius: 12px !important;
    padding: 0.75rem !important; background: #fafafa !important;
    box-shadow: none !important;
}
.card-col.selected {
    border: 5px solid #16a34a !important; background: #f0fdf4 !important;
    box-shadow: 0 0 0 3px #bbf7d0 !important;
}
.card-col .block, .card-col .form {
    background: transparent !important; border: none !important;
    box-shadow: none !important; padding: 0 !important; margin: 0 !important;
}
.candidate-label { text-align: center; font-weight: 600; color: #374151; margin: 0 0 0.35rem !important; }
.candidate-label .block, .candidate-label .prose { margin: 0 !important; padding: 0 !important; }
.candidate-photo .image-container {
    height: auto !important; min-height: 0 !important; min-width: 0 !important;
}
.candidate-photo .image-container button {
    height: auto !important; min-height: 0 !important; padding: 0 !important;
}
.candidate-photo .image-frame {
    height: auto !important; width: 100% !important;
}
.candidate-photo .image-frame img {
    max-height: 280px !important; width: auto !important; height: auto !important;
    max-width: 100% !important; object-fit: scale-down !important;
    border-radius: 8px !important; display: block !important; margin: 0 auto !important;
}
.select-btn { margin-top: 0.5rem !important; }
.select-btn button {
    width: 100% !important; min-height: 2.6rem !important; font-weight: 600 !important;
    border-radius: 8px !important; font-size: 0.95rem !important;
}
.select-btn-off button {
    background: #f0f9ff !important; border: 1px solid #60a5fa !important; color: #1d4ed8 !important;
}
.select-btn-on button {
    background: #22c55e !important; border: 1px solid #16a34a !important; color: white !important;
}
.accepted-count {
    text-align: center; font-size: 1.05rem; margin: 1.25rem 0 0.5rem; color: #374151;
}
.status-message { text-align: center; min-height: 1.25rem; font-weight: 600; margin-bottom: 0.25rem; }
.status-ok { color: #166534; }
.status-error { color: #b91c1c; }
.actions-row {
    justify-content: center !important; gap: 0.75rem !important;
    max-width: 560px !important; margin: 0.75rem auto 0 !important;
}
.actions-row > div { flex: 1 1 0 !important; min-width: 0 !important; }
.actions-row button { width: 100% !important; min-height: 2.75rem !important; border-radius: 8px !important; }
.primary-btn button {
    background: #2563eb !important; border-color: #1d4ed8 !important; color: white !important;
    font-weight: 600 !important;
}
.secondary-btn button {
    background: white !important; border: 1px solid #d1d5db !important; color: #374151 !important;
    font-weight: 500 !important;
}
.all-done-row { max-width: 560px !important; margin: 0.5rem auto 0 !important; }
.all-done-row button {
    width: 100% !important; background: transparent !important; border: none !important;
    color: #6b7280 !important; text-decoration: underline !important; box-shadow: none !important;
}
.complete-box { text-align: center; padding: 2.5rem 1rem; }
.complete-actions { max-width: 280px !important; margin: 1rem auto 0 !important; }
"""
