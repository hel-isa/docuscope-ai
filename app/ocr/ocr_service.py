from __future__ import annotations

from pathlib import Path

import pytesseract
from pdf2image import convert_from_path

from app.config import MAX_IMAGE_PIXELS
from app.security.resource_guards import configure_pillow_limits, open_image_safely

configure_pillow_limits(MAX_IMAGE_PIXELS)


def ocr_image(file_path: str | Path) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found for OCR: {path}")

    img = open_image_safely(path, MAX_IMAGE_PIXELS)
    return pytesseract.image_to_string(img).strip()


def ocr_pdf(file_path: str | Path, max_pages: int = 10) -> str:
    """
    OCR a PDF by converting pages to images.
    For MVP, limit OCR to the first max_pages pages to avoid very slow runs.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF file not found for OCR: {path}")

    images = convert_from_path(str(path), first_page=1, last_page=max_pages)
    text_parts: list[str] = []

    for img in images:
        page_text = pytesseract.image_to_string(img).strip()
        if page_text:
            text_parts.append(page_text)

    return "\n".join(text_parts).strip()
