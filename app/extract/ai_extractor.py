from __future__ import annotations

from typing import Any


def extract_fields_with_ai_fallback(sanitized_text: str, doc_class: str) -> dict[str, Any]:
    """
    MVP placeholder.
    Later replace with a real model call.
    """
    text = sanitized_text.lower()
    fields: dict[str, Any] = {}

    if doc_class == "resume":
        fields["education_present"] = "education" in text
        fields["experience_present"] = "experience" in text
        fields["skills_present"] = "skills" in text

    if doc_class == "letter":
        if "dear" in text:
            fields["formal_greeting_present"] = True

    return fields
