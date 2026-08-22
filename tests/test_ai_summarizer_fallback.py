from app.ai.provider import AIProviderError
from app.summarize.ai_summarizer import generate_sanitized_summary


class _FakeProvider:
    def __init__(self, result=None, error=None) -> None:
        self._result = result
        self._error = error

    def summarize(self, sanitized_text: str, doc_class: str) -> str:
        if self._error is not None:
            raise self._error
        return self._result


def test_no_provider_falls_back_to_template(monkeypatch) -> None:
    monkeypatch.setattr("app.summarize.ai_summarizer.get_provider", lambda: None)

    summary = generate_sanitized_summary("irrelevant text", "invoice")

    assert summary == "Invoice-like document containing dates, references, and financial information."


def test_working_provider_is_used(monkeypatch) -> None:
    fake = _FakeProvider(result="A neutral AI-generated summary.")
    monkeypatch.setattr("app.summarize.ai_summarizer.get_provider", lambda: fake)

    summary = generate_sanitized_summary("irrelevant text", "invoice")

    assert summary == "A neutral AI-generated summary."


def test_provider_error_falls_back_to_template(monkeypatch) -> None:
    fake = _FakeProvider(error=AIProviderError("boom"))
    monkeypatch.setattr("app.summarize.ai_summarizer.get_provider", lambda: fake)

    summary = generate_sanitized_summary("irrelevant text", "contract")

    assert summary.startswith("Contract-like document")
