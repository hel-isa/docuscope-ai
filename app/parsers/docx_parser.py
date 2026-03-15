from __future__ import annotations

from pathlib import Path

from docx import Document


def parse_docx(file_path: str | Path) -> dict:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"DOCX file not found: {path}")

    doc = Document(str(path))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    text = "\n".join(paragraphs)

    core = doc.core_properties
    embedded_metadata = {
        "author": core.author,
        "title": core.title,
        "subject": core.subject,
        "category": core.category,
        "comments": core.comments,
        "last_modified_by": core.last_modified_by,
    }

    return {
        "text": text,
        "page_count": None,
        "author_safe": core.author,
        "embedded_metadata": {k: v for k, v in embedded_metadata.items() if v},
        "ocr_needed": False,
        "ocr_used": False,
        "tables_detected": False,
        "signatures_detected": False,
        "stamps_detected": False,
    }
