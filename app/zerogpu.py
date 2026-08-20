"""ZeroGPU compatibility for Hugging Face Spaces (Phase 0 has no GPU work)."""

from __future__ import annotations

import spaces


@spaces.GPU(duration=1)
def startup_probe() -> None:
    """Registered with Gradio so ZeroGPU passes its startup scan.

    Phase 0 is Supabase + static images only; this is never invoked in normal use.
    """
    return None
