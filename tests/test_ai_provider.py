import json

import anthropic
import httpx
import pytest

from app.ai.anthropic_provider import AnthropicProvider
from app.ai.provider import AIProviderError, AIProviderInvalidResponse, AIProviderTimeout


class _FakeResponse:
    def __init__(self, text: str, stop_reason: str = "end_turn", stop_details=None) -> None:
        self.content = [anthropic.types.TextBlock(text=text, type="text")]
        self.stop_reason = stop_reason
        self.stop_details = stop_details


class _FakeMessages:
    def __init__(self, response=None, error=None) -> None:
        self._response = response
        self._error = error
        self.last_kwargs: dict | None = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        if self._error is not None:
            raise self._error
        return self._response


class _FakeClient:
    def __init__(self, response=None, error=None) -> None:
        self.messages = _FakeMessages(response=response, error=error)


def _provider_with(response=None, error=None) -> AnthropicProvider:
    provider = AnthropicProvider(
        api_key="fake-key", model="claude-haiku-4-5-20251001", timeout_seconds=5, max_retries=0
    )
    provider._client = _FakeClient(response=response, error=error)
    return provider


def test_classify_happy_path() -> None:
    payload = json.dumps({"label": "invoice", "confidence": 0.91})
    provider = _provider_with(response=_FakeResponse(payload))

    result = provider.classify("Invoice #123 total $50")

    assert result.label == "invoice"
    assert result.confidence == 0.91
    assert result.source == "ai_claude"


def test_extract_fields_happy_path() -> None:
    payload = json.dumps({"fields": {"invoice_number": "INV-1", "total": "50.00"}})
    provider = _provider_with(response=_FakeResponse(payload))

    fields = provider.extract_fields("Invoice #123", "invoice")

    assert fields == {"invoice_number": "INV-1", "total": "50.00"}


def test_summarize_happy_path() -> None:
    payload = json.dumps({"summary": "An invoice document with a total amount."})
    provider = _provider_with(response=_FakeResponse(payload))

    summary = provider.summarize("Invoice #123", "invoice")

    assert summary == "An invoice document with a total amount."


def test_malformed_json_raises_invalid_response() -> None:
    provider = _provider_with(response=_FakeResponse("not json"))

    with pytest.raises(AIProviderInvalidResponse):
        provider.classify("some text")


def test_hallucinated_label_raises_invalid_response() -> None:
    payload = json.dumps({"label": "not_a_real_class", "confidence": 0.5})
    provider = _provider_with(response=_FakeResponse(payload))

    with pytest.raises(AIProviderInvalidResponse):
        provider.classify("some text")


def test_summary_containing_pii_raises_invalid_response() -> None:
    payload = json.dumps({"summary": "Contact john.smith@example.com for details."})
    provider = _provider_with(response=_FakeResponse(payload))

    with pytest.raises(AIProviderInvalidResponse):
        provider.summarize("some text", "letter")


def test_timeout_raises_ai_provider_timeout() -> None:
    error = anthropic.APITimeoutError(request=object())
    provider = _provider_with(error=error)

    with pytest.raises(AIProviderTimeout):
        provider.classify("some text")


def test_rate_limit_raises_ai_provider_error() -> None:
    fake_response = httpx.Response(
        status_code=429, request=httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    )
    error = anthropic.RateLimitError("rate limited", response=fake_response, body=None)
    provider = _provider_with(error=error)

    with pytest.raises(AIProviderError):
        provider.classify("some text")


def test_no_text_block_raises_invalid_response() -> None:
    response = _FakeResponse.__new__(_FakeResponse)
    response.content = []
    response.stop_reason = "end_turn"
    response.stop_details = None
    provider = _provider_with(response=response)

    with pytest.raises(AIProviderInvalidResponse):
        provider.classify("some text")


def test_refusal_raises_invalid_response_with_category() -> None:
    class _FakeStopDetails:
        category = "general_harms"

    response = _FakeResponse("", stop_reason="refusal", stop_details=_FakeStopDetails())
    provider = _provider_with(response=response)

    with pytest.raises(AIProviderInvalidResponse, match="refusal"):
        provider.classify("some text")


def test_max_tokens_truncation_raises_invalid_response() -> None:
    response = _FakeResponse('{"label": "invoi', stop_reason="max_tokens")
    provider = _provider_with(response=response)

    with pytest.raises(AIProviderInvalidResponse, match="truncated"):
        provider.classify("some text")
