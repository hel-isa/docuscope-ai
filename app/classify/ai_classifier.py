from __future__ import annotations


def classify_with_ai_fallback(sanitized_text: str) -> dict:
    """
    MVP placeholder.
    Later you can replace this with a real LLM/local model.
    """
    text = sanitized_text.lower()

    if "invoice" in text:
        return {"label": "invoice", "confidence": 0.80, "source": "ai"}

    if "experience" in text and "education" in text:
        return {"label": "resume", "confidence": 0.78, "source": "ai"}

    if "agreement" in text or "contract" in text:
        return {"label": "contract", "confidence": 0.78, "source": "ai"}

    if "balance" in text and "account" in text:
        return {"label": "bank_statement", "confidence": 0.76, "source": "ai"}

    return {"label": "unknown", "confidence": 0.50, "source": "ai"}
