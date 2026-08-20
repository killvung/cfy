"""Generate labeled placeholder JPEGs for Phase 0 static evaluation."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "static" / "cat_a"

COLORS = [
    (230, 126, 34),
    (52, 152, 219),
    (46, 204, 113),
    (155, 89, 182),
]


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for index, color in enumerate(COLORS, start=1):
        image = Image.new("RGB", (512, 512), color=color)
        draw = ImageDraw.Draw(image)
        label = f"Cat A — Candidate {index:02d}"
        draw.rectangle([(24, 24), (488, 488)], outline=(255, 255, 255), width=4)
        draw.text((48, 220), label, fill=(255, 255, 255))
        draw.text((48, 260), "Phase 0 placeholder", fill=(255, 255, 255))
        output_path = OUTPUT_DIR / f"{index:02d}.jpg"
        image.save(output_path, format="JPEG", quality=90)
        print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
