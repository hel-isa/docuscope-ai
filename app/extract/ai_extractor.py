from __future__ import annotations

from typing import Any

from app.ai.provider import get_provider


def _extract_fields_keyword_fallback(sanitized_text: str, doc_class: str) -> dict[str, Any]:
    """
    Deterministic fallback used when no AI provider is configured, or when
    the AI call fails for any reason.
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


def extract_fields_with_ai_fallback(sanitized_text: str, doc_class: str) -> dict[str, Any]:
    provider = get_provider()
    if provider is None:
        return _extract_fields_keyword_fallback(sanitized_text, doc_class)

    try:
        return provider.extract_fields(sanitized_text, doc_class)
    except Exception:
        # See app/classify/ai_classifier.py for why this is a broad catch.
        return _extract_fields_keyword_fallback(sanitized_text, doc_class)
