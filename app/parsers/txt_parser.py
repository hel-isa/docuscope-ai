from __future__ import annotations

from pathlib import Path


def parse_txt(file_path: str | Path) -> dict:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"TXT file not found: {path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    text = path.read_text(encoding="utf-8", errors="ignore")

    return {
        "text": text,
        "page_count": 1,
        "author_safe": None,
        "embedded_metadata": {},
        "ocr_needed": False,
        "ocr_used": False,
        "tables_detected": False,
        "signatures_detected": False,
        "stamps_detected": False,
    }
