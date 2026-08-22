from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from app.config import MAX_PDF_PAGES
from app.ocr.ocr_service import ocr_pdf
from app.security.resource_guards import PdfTooManyPagesError, check_pdf_page_count


def parse_pdf(file_path: str | Path) -> dict:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    parse_status = "ok"
    risk_flags: list[str] = []

    try:
        reader = PdfReader(str(path))
    except Exception as e:
        parse_status = "warning"
        risk_flags.append("pdf_structure_warning")
        raise ValueError(f"Could not open PDF: {path}: {e}") from e

    try:
        page_count = len(reader.pages)
    except Exception:
        # Unknown page count is not the same as "safe" — do not default to 0,
        # which would trivially pass the guard below. Leave it unset and rely
        # on the hard cap enforced during iteration instead.
        page_count = None
        parse_status = "warning"
        risk_flags.append("pdf_structure_warning")

    if page_count is not None:
        check_pdf_page_count(page_count, MAX_PDF_PAGES)

    text_parts: list[str] = []
    pages_seen = 0
    try:
        for page in reader.pages:
            pages_seen += 1
            if pages_seen > MAX_PDF_PAGES:
                # Authoritative enforcement: catches the case where the
                # upfront len(reader.pages) count was wrong/unavailable but
                # the page tree still yields more pages than allowed.
                raise PdfTooManyPagesError(
                    f"PDF exceeded the page limit during extraction: "
                    f"more than {MAX_PDF_PAGES} pages ({path.name})"
                )
            try:
                page_text = page.extract_text() or ""
                text_parts.append(page_text)
            except Exception:
                text_parts.append("")
    except PdfTooManyPagesError:
        raise
    except Exception:
        parse_status = "warning"
        risk_flags.append("pdf_structure_warning")

    if page_count is None:
        page_count = pages_seen or len(text_parts)

    full_text = "\n".join(text_parts).strip()

    embedded_metadata = {}
    author_safe = None

    try:
        if reader.metadata:
            embedded_metadata = {
                str(key).lstrip("/"): str(value)
                for key, value in reader.metadata.items()
                if value is not None
            }
            author_safe = embedded_metadata.get("Author")
    except Exception:
        parse_status = "warning"
        risk_flags.append("pdf_structure_warning")

    ocr_needed = len(full_text) < 50
    ocr_used = False

    if ocr_needed:
        ocr_text = ocr_pdf(path)
        if ocr_text:
            full_text = ocr_text
            ocr_used = True

    return {
        "text": full_text,
        "page_count": page_count,
        "author_safe": author_safe,
        "embedded_metadata": embedded_metadata,
        "ocr_needed": ocr_needed,
        "ocr_used": ocr_used,
        "tables_detected": False,
        "signatures_detected": False,
        "stamps_detected": False,
        "parse_status": parse_status,
        "risk_flags": risk_flags,
    }
