from __future__ import annotations

from app.ai.provider import get_provider


def _classify_with_keyword_fallback(sanitized_text: str) -> dict:
    """
    Deterministic fallback used when no AI provider is configured, or when
    the AI call fails for any reason. Keeps the pipeline fully functional
    with zero external dependencies.
    """
    text = sanitized_text.lower()

    if "invoice" in text:
        return {"label": "invoice", "confidence": 0.80, "source": "ai_keyword_fallback"}

    if "experience" in text and "education" in text:
        return {"label": "resume", "confidence": 0.78, "source": "ai_keyword_fallback"}

    if "agreement" in text or "contract" in text:
        return {"label": "contract", "confidence": 0.78, "source": "ai_keyword_fallback"}

    if "balance" in text and "account" in text:
        return {"label": "bank_statement", "confidence": 0.76, "source": "ai_keyword_fallback"}

    return {"label": "unknown", "confidence": 0.50, "source": "ai_keyword_fallback"}


def classify_with_ai_fallback(sanitized_text: str) -> dict:
    provider = get_provider()
    if provider is None:
        return _classify_with_keyword_fallback(sanitized_text)

    try:
        info = provider.classify(sanitized_text)
    except Exception:
        # The AI layer is a best-effort enhancement, not a dependency: any
        # failure here (typed AIProviderError, or an unexpected error from a
        # misbehaving provider) must degrade to the deterministic fallback
        # rather than ever crash or skip processing of this document.
        return _classify_with_keyword_fallback(sanitized_text)

    return {"label": info.label, "confidence": info.confidence, "source": info.source}
