from app.ai.provider import AIProviderError
from app.extract.ai_extractor import extract_fields_with_ai_fallback


class _FakeProvider:
    def __init__(self, result=None, error=None) -> None:
        self._result = result
        self._error = error

    def extract_fields(self, sanitized_text: str, doc_class: str):
        if self._error is not None:
            raise self._error
        return self._result


def test_no_provider_falls_back_to_keywords(monkeypatch) -> None:
    monkeypatch.setattr("app.extract.ai_extractor.get_provider", lambda: None)

    fields = extract_fields_with_ai_fallback("education and experience listed", "resume")

    assert fields["education_present"] is True
    assert fields["experience_present"] is True


def test_working_provider_is_used(monkeypatch) -> None:
    fake = _FakeProvider(result={"invoice_number": "INV-99"})
    monkeypatch.setattr("app.extract.ai_extractor.get_provider", lambda: fake)

    fields = extract_fields_with_ai_fallback("irrelevant text", "invoice")

    assert fields == {"invoice_number": "INV-99"}


def test_provider_error_falls_back_to_keywords(monkeypatch) -> None:
    fake = _FakeProvider(error=AIProviderError("boom"))
    monkeypatch.setattr("app.extract.ai_extractor.get_provider", lambda: fake)

    fields = extract_fields_with_ai_fallback("Dear Sir,", "letter")

    assert fields == {"formal_greeting_present": True}
