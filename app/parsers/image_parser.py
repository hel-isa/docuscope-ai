from __future__ import annotations

from pathlib import Path

from app.config import MAX_IMAGE_PIXELS
from app.ocr.ocr_service import ocr_image
from app.security.resource_guards import configure_pillow_limits, open_image_safely

configure_pillow_limits(MAX_IMAGE_PIXELS)


def parse_image(file_path: str | Path) -> dict:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {path}")

    img = open_image_safely(path, MAX_IMAGE_PIXELS)
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
