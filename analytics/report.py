"""Batch analytics: acceptance rate from Supabase feedback."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "analytics" / "output"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import get_client as _get_client  # noqa: E402


def _fetch_feedback_rows(client) -> pd.DataFrame:
    response = (
        client.table("feedback")
        .select(
            "accepted, submitted_at, "
            "sessions(id, invites(evaluator_label)), "
            "evaluation_tasks(test_id, batch_id, cats(slug, display_name)), "
            "images(id, local_path, seed, base_model, lora_version)"
        )
        .execute()
    )
    rows = response.data or []
    if not rows:
        return pd.DataFrame()

    flat_rows = []
    for row in rows:
        session = row.get("sessions") or {}
        invite = session.get("invites") or {}
        task = row.get("evaluation_tasks") or {}
        cat = task.get("cats") or {}
        image = row.get("images") or {}
        flat_rows.append(
            {
                "accepted": row["accepted"],
                "submitted_at": row["submitted_at"],
                "evaluator_label": invite.get("evaluator_label"),
                "test_id": task.get("test_id"),
                "batch_id": task.get("batch_id"),
                "cat_slug": cat.get("slug"),
                "cat_display_name": cat.get("display_name"),
                "image_id": image.get("id"),
                "local_path": image.get("local_path"),
                "seed": image.get("seed"),
                "base_model": image.get("base_model"),
                "lora_version": image.get("lora_version"),
            }
        )

    return pd.DataFrame(flat_rows)


def _acceptance_rate(series: pd.Series) -> float:
    if series.empty:
        return 0.0
    return float(series.sum()) / float(len(series))


def _print_section(title: str, df: pd.DataFrame) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    if df.empty:
        print("(no data)")
        return
    print(df.to_string(index=False))


def _plot_by_evaluator(df: pd.DataFrame, output_path: Path) -> None:
    if df.empty:
        return

    grouped = (
        df.groupby("evaluator_label", dropna=False)["accepted"]
        .agg(accepted="sum", shown="count")
        .reset_index()
    )
    grouped["acceptance_rate"] = grouped["accepted"] / grouped["shown"]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(grouped["evaluator_label"], grouped["acceptance_rate"], color="#4C78A8")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Acceptance rate")
    ax.set_xlabel("Evaluator")
    ax.set_title("Acceptance rate by evaluator")
    for index, row in grouped.iterrows():
        ax.text(
            index,
            row["acceptance_rate"] + 0.02,
            f"{row['acceptance_rate']:.0%}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def main() -> None:
    client = _get_client()
    df = _fetch_feedback_rows(client)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if df.empty:
        print(
            "No feedback rows found. Run the Gradio app and submit feedback first."
        )
        return

    overall_rate = _acceptance_rate(df["accepted"])
    print(
        f"Overall acceptance rate: {overall_rate:.1%} ({int(df['accepted'].sum())}/{len(df)})"
    )

    by_evaluator = (
        df.groupby("evaluator_label", dropna=False)["accepted"]
        .agg(accepted="sum", shown="count")
        .reset_index()
    )
    by_evaluator["acceptance_rate"] = by_evaluator["accepted"] / by_evaluator["shown"]
    _print_section("By evaluator", by_evaluator)

    by_image = (
        df.groupby(["image_id", "local_path", "seed"], dropna=False)["accepted"]
        .agg(accepted="sum", shown="count")
        .reset_index()
    )
    by_image["acceptance_rate"] = by_image["accepted"] / by_image["shown"]
    _print_section("By image", by_image)

    chart_path = OUTPUT_DIR / "acceptance_by_evaluator.png"
    _plot_by_evaluator(df, chart_path)
    print(f"\nSaved chart: {chart_path}")


if __name__ == "__main__":
    main()
