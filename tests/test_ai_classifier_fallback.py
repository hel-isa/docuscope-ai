from app.ai.provider import AIProviderError
from app.classify.ai_classifier import classify_with_ai_fallback
from app.models.fingerprint import ClassificationInfo


class _FakeProvider:
    def __init__(self, result=None, error=None) -> None:
        self._result = result
        self._error = error

    def classify(self, sanitized_text: str) -> ClassificationInfo:
        if self._error is not None:
            raise self._error
        return self._result


def test_no_provider_falls_back_to_keywords(monkeypatch) -> None:
    monkeypatch.setattr("app.classify.ai_classifier.get_provider", lambda: None)

    result = classify_with_ai_fallback("This is an invoice for services rendered.")

    assert result["label"] == "invoice"
    assert result["source"] == "ai_keyword_fallback"


def test_working_provider_is_used(monkeypatch) -> None:
    fake = _FakeProvider(result=ClassificationInfo(label="contract", confidence=0.93, source="ai_claude"))
    monkeypatch.setattr("app.classify.ai_classifier.get_provider", lambda: fake)

    result = classify_with_ai_fallback("irrelevant text")

    assert result == {"label": "contract", "confidence": 0.93, "source": "ai_claude"}


def test_provider_error_falls_back_to_keywords(monkeypatch) -> None:
    fake = _FakeProvider(error=AIProviderError("boom"))
    monkeypatch.setattr("app.classify.ai_classifier.get_provider", lambda: fake)

    result = classify_with_ai_fallback("This mentions a contract agreement.")

    assert result["label"] == "contract"
    assert result["source"] == "ai_keyword_fallback"
