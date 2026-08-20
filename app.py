"""Hugging Face Space entrypoint for the cat image review app."""

import gradio as gr

from app.app import create_app
from app.styles import CUSTOM_CSS

demo = create_app()

if __name__ == "__main__":
    demo.launch(css=CUSTOM_CSS, theme=gr.themes.Soft())
