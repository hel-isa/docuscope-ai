from __future__ import annotations

import json
from typing import Any

import anthropic
import pydantic

from app.ai.prompts import (
    CLASSIFY_SYSTEM_PROMPT,
    EXTRACT_SYSTEM_PROMPT,
    SUMMARIZE_SYSTEM_PROMPT,
    build_user_message,
)
from app.ai.provider import AIProviderError, AIProviderInvalidResponse, AIProviderTimeout
from app.ai.schemas import (
    CLASSIFICATION_JSON_SCHEMA,
    EXTRACTION_JSON_SCHEMA,
    SUMMARY_JSON_SCHEMA,
    AIClassificationResult,
    AIExtractionResult,
    AISummaryResult,
)
from app.models.fingerprint import ClassificationInfo

_MAX_OUTPUT_TOKENS = 1024


class AnthropicProvider:
    """Concrete AIProvider backed by the Anthropic Claude API. Isolates the
    `anthropic` SDK to this one module: callers only ever see this class's
    methods and the AIProviderError hierarchy, never SDK exceptions or
    response objects directly."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        timeout_seconds: float,
        max_retries: int,
    ) -> None:
        self._model = model
        self._client = anthropic.Anthropic(
            api_key=api_key,
            timeout=timeout_seconds,
            max_retries=max_retries,
        )

    def classify(self, sanitized_text: str) -> ClassificationInfo:
        payload = self._request(
            system_prompt=CLASSIFY_SYSTEM_PROMPT,
            user_message=build_user_message(sanitized_text),
            json_schema=CLASSIFICATION_JSON_SCHEMA,
        )
        try:
            result = AIClassificationResult.model_validate(payload)
        except pydantic.ValidationError as exc:
            raise AIProviderInvalidResponse(f"Invalid classification response: {exc}") from exc

        return ClassificationInfo(label=result.label, confidence=result.confidence, source="ai_claude")

    def extract_fields(self, sanitized_text: str, doc_class: str) -> dict[str, Any]:
        payload = self._request(
            system_prompt=EXTRACT_SYSTEM_PROMPT,
            user_message=build_user_message(sanitized_text, doc_class=doc_class),
            json_schema=EXTRACTION_JSON_SCHEMA,
        )
        try:
            result = AIExtractionResult.model_validate(payload)
        except pydantic.ValidationError as exc:
            raise AIProviderInvalidResponse(f"Invalid extraction response: {exc}") from exc

        return result.fields

    def summarize(self, sanitized_text: str, doc_class: str) -> str:
        payload = self._request(
            system_prompt=SUMMARIZE_SYSTEM_PROMPT,
            user_message=build_user_message(sanitized_text, doc_class=doc_class),
            json_schema=SUMMARY_JSON_SCHEMA,
        )
        try:
            result = AISummaryResult.model_validate(payload)
        except pydantic.ValidationError as exc:
            raise AIProviderInvalidResponse(f"Invalid summary response: {exc}") from exc

        return result.summary

    def _request(
        self,
        *,
        system_prompt: str,
        user_message: str,
        json_schema: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=_MAX_OUTPUT_TOKENS,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
                output_config={"format": {"type": "json_schema", "schema": json_schema}},
            )
        except anthropic.APITimeoutError as exc:
            raise AIProviderTimeout("Anthropic API request timed out") from exc
        except (anthropic.APIConnectionError, anthropic.APIStatusError, anthropic.AnthropicError) as exc:
            raise AIProviderError(f"Anthropic API request failed: {exc}") from exc

        if response.stop_reason == "refusal":
            category = response.stop_details.category if response.stop_details else None
            raise AIProviderInvalidResponse(f"Anthropic declined to respond (refusal, category={category})")

        if response.stop_reason == "max_tokens":
            raise AIProviderInvalidResponse(
                f"Anthropic response was truncated at the {_MAX_OUTPUT_TOKENS}-token output limit"
            )

        text = self._extract_text(response)

        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise AIProviderInvalidResponse(f"Anthropic response was not valid JSON: {exc}") from exc

    @staticmethod
    def _extract_text(response: anthropic.types.Message) -> str:
        for block in response.content:
            if isinstance(block, anthropic.types.TextBlock):
                return block.text
        raise AIProviderInvalidResponse("Anthropic response contained no text content block")
