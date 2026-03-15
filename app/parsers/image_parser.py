from __future__ import annotations

from pathlib import Path

from PIL import Image

from app.ocr.ocr_service import ocr_image


def parse_image(file_path: str | Path) -> dict:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {path}")

    img = Image.open(path)
    text = ocr_image(path)

    return {
        "text": text,
        "page_count": 1,
        "author_safe": None,
        "embedded_metadata": {
            "width": img.width,
            "height": img.height,
            "mode": img.mode,
            "format": img.format,
        },
        "ocr_needed": True,
        "ocr_used": True,
        "tables_detected": False,
        "signatures_detected": False,
        "stamps_detected": False,
    }
