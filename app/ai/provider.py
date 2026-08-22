from __future__ import annotations

from typing import Any, Protocol

from app import config
from app.models.fingerprint import ClassificationInfo


class AIProviderError(Exception):
    """Base class for all AI-provider failures. Callers should catch this
    (never a specific SDK exception) and fall back to rules-based logic."""


class AIProviderUnavailable(AIProviderError):
    """No provider is configured (disabled, or no API key set)."""


class AIProviderTimeout(AIProviderError):
    """The provider did not respond within the configured timeout."""


class AIProviderInvalidResponse(AIProviderError):
    """The provider responded, but its output failed schema validation."""


class AIProvider(Protocol):
    """Provider-agnostic interface for the GenAI fallback layer. Every method
    receives already-sanitized (PII-masked) text and must never be given raw
    document content. A concrete implementation (e.g. a local-model provider)
    only needs to satisfy this interface and raise the exceptions above."""

    def classify(self, sanitized_text: str) -> ClassificationInfo: ...

    def extract_fields(self, sanitized_text: str, doc_class: str) -> dict[str, Any]: ...

    def summarize(self, sanitized_text: str, doc_class: str) -> str: ...


_provider_instance: AIProvider | None = None
_provider_initialized = False


def get_provider() -> AIProvider | None:
    """Single choke point for "is AI available right now". Returns None when
    AI is disabled or no API key is configured, otherwise a cached provider
    instance. This is the seam tests monkeypatch instead of touching the
    Anthropic SDK directly."""
    global _provider_instance, _provider_initialized

    if _provider_initialized:
        return _provider_instance

    _provider_initialized = True

    if not config.AI_ENABLED or not config.ANTHROPIC_API_KEY:
        _provider_instance = None
        return None

    from app.ai.anthropic_provider import AnthropicProvider

    _provider_instance = AnthropicProvider(
        api_key=config.ANTHROPIC_API_KEY,
        model=config.ANTHROPIC_MODEL,
        timeout_seconds=config.ANTHROPIC_TIMEOUT_SECONDS,
        max_retries=config.ANTHROPIC_MAX_RETRIES,
    )
    return _provider_instance


def reset_provider_cache() -> None:
    """Test-only helper: clears the cached provider so get_provider() re-reads
    config on the next call."""
    global _provider_instance, _provider_initialized
    _provider_instance = None
    _provider_initialized = False
