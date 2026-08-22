from __future__ import annotations

DOCUMENT_CLASSES: frozenset[str] = frozenset(
    {
        "invoice",
        "receipt",
        "contract",
        "resume",
        "bank_statement",
        "tax_document",
        "form",
        "letter",
        "unknown",
    }
)
