from __future__ import annotations

from pathlib import Path

import pytesseract
from PIL import Image
from pdf2image import convert_from_path


def ocr_image(file_path: str | Path) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found for OCR: {path}")

    img = Image.open(path)
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
