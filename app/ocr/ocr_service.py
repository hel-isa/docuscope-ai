from __future__ import annotations

from pathlib import Path

import pytesseract
from PIL import Image


def ocr_image(file_path: str | Path) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found for OCR: {path}")

    img = Image.open(path)
    return pytesseract.image_to_string(img).strip()
