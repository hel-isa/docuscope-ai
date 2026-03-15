from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class FileInfo(BaseModel):
    file_name: str
    full_path: str
    file_extension: str
    mime_type: str
    file_size_bytes: int
    created_at_fs: Optional[datetime] = None
    modified_at_fs: Optional[datetime] = None
    sha256_hash: str


class MetadataInfo(BaseModel):
    page_count: Optional[int] = None
    language: Optional[str] = None
    author_safe: Optional[str] = None
    embedded_metadata: dict[str, Any] = Field(default_factory=dict)


class ExtractionInfo(BaseModel):
    ocr_needed: bool = False
    ocr_used: bool = False
    tables_detected: bool = False
    signatures_detected: bool = False
    stamps_detected: bool = False


class PrivacyInfo(BaseModel):
    pii_detected: bool = False
    pii_types: list[str] = Field(default_factory=list)
    pii_count: int = 0
    masked_entities: dict[str, Any] = Field(default_factory=dict)


class ClassificationInfo(BaseModel):
    label: str = "unknown"
    confidence: float = 0.0
    source: str = "rules"


class DuplicateInfo(BaseModel):
    exact_duplicate: bool = False
    exact_duplicate_of: Optional[str] = None


class RiskInfo(BaseModel):
    risk_flags: list[str] = Field(default_factory=list)
    anomaly_flags: list[str] = Field(default_factory=list)


class ConfidenceInfo(BaseModel):
    overall: float = 0.0
    classification: float = 0.0
    extraction: float = 0.0
    ocr: float = 0.0


class ReviewInfo(BaseModel):
    human_review_required: bool = False
    reason: Optional[str] = None


class DocumentFingerprint(BaseModel):
    document_id: str = Field(default_factory=lambda: str(uuid4()))
    privacy_mode: str = "strict"
    raw_text_persisted: bool = False
    redaction_applied: bool = True

    file_info: FileInfo
    metadata: MetadataInfo = Field(default_factory=MetadataInfo)
    extraction: ExtractionInfo = Field(default_factory=ExtractionInfo)
    privacy: PrivacyInfo = Field(default_factory=PrivacyInfo)
    classification: ClassificationInfo = Field(default_factory=ClassificationInfo)

    keywords: list[str] = Field(default_factory=list)
    title_sanitized: Optional[str] = None
    sanitized_summary: Optional[str] = None
    document_specific_fields: dict[str, Any] = Field(default_factory=dict)

    duplicate: DuplicateInfo = Field(default_factory=DuplicateInfo)
    risk: RiskInfo = Field(default_factory=RiskInfo)
    confidence: ConfidenceInfo = Field(default_factory=ConfidenceInfo)
    review: ReviewInfo = Field(default_factory=ReviewInfo)

    parse_status: str = "success"
    error_message_safe: Optional[str] = None
