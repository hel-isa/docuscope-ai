from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from app.classify.constants import DOCUMENT_CLASSES
from app.privacy.pii_detector import detect_pii

MAX_SUMMARY_LENGTH = 600
MAX_EXTRACTION_FIELDS = 20


class AIClassificationResult(BaseModel):
    """Validated shape of Claude's classification response. `source` is
    intentionally not a field here: provenance is always set by the calling
    provider code, never taken from model output."""

    label: str
    confidence: float = Field(ge=0.0, le=1.0)

    @field_validator("label")
    @classmethod
    def label_must_be_known(cls, value: str) -> str:
        if value not in DOCUMENT_CLASSES:
            raise ValueError(f"Unknown document class: {value!r}")
        return value


class AIExtractionResult(BaseModel):
    """Deliberately restricted to a flat string-to-string map (no nested
    objects, arrays, or mixed value types) for two reasons: it can't pollute
    `document_specific_fields` with arbitrary structure, and it renders as a
    simple, widely-supported JSON schema shape for structured-output
    generation — a heterogeneous value-type union is a much less common
    schema pattern and a real risk of provider incompatibility."""

    fields: dict[str, str] = Field(default_factory=dict, max_length=MAX_EXTRACTION_FIELDS)


class AISummaryResult(BaseModel):
    """Belt-and-suspenders check: even though the model only ever sees
    already-masked input, this rejects any output that looks like it
    reconstructed or hallucinated PII, per SECURITY.md's commitment to verify
    that redaction actually held."""

    summary: str = Field(max_length=MAX_SUMMARY_LENGTH)

    @field_validator("summary")
    @classmethod
    def summary_must_not_contain_pii(cls, value: str) -> str:
        pii = detect_pii(value)
        if pii["pii_detected"]:
            raise ValueError(
                f"AI summary output appears to contain PII-shaped content: {pii['pii_types']}"
            )
        return value


CLASSIFICATION_JSON_SCHEMA = AIClassificationResult.model_json_schema()
EXTRACTION_JSON_SCHEMA = AIExtractionResult.model_json_schema()
SUMMARY_JSON_SCHEMA = AISummaryResult.model_json_schema()
