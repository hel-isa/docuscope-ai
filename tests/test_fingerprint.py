import pytest
from datetime import datetime
from app.models.fingerprint import (
    FileInfo,
    MetadataInfo,
    ExtractionInfo,
    PrivacyInfo,
    ClassificationInfo,
    DuplicateInfo,
)


class TestFileInfo:
    def test_create_file_info(self):
        file_info = FileInfo(
            file_name="test.pdf",
            full_path="/path/to/test.pdf",
            file_extension=".pdf",
            mime_type="application/pdf",
            file_size_bytes=1024,
            sha256_hash="abc123",
        )
        assert file_info.file_name == "test.pdf"
        assert file_info.full_path == "/path/to/test.pdf"
        assert file_info.file_extension == ".pdf"
        assert file_info.mime_type == "application/pdf"
        assert file_info.file_size_bytes == 1024
        assert file_info.sha256_hash == "abc123"
        assert file_info.created_at_fs is None
        assert file_info.modified_at_fs is None

    def test_file_info_with_timestamps(self):
        created = datetime(2023, 1, 1, 12, 0, 0)
        modified = datetime(2023, 1, 2, 12, 0, 0)
        file_info = FileInfo(
            file_name="test.pdf",
            full_path="/path/to/test.pdf",
            file_extension=".pdf",
            mime_type="application/pdf",
            file_size_bytes=1024,
            sha256_hash="abc123",
            created_at_fs=created,
            modified_at_fs=modified,
        )
        assert file_info.created_at_fs == created
        assert file_info.modified_at_fs == modified


class TestMetadataInfo:
    def test_create_metadata_info(self):
        metadata = MetadataInfo(
            page_count=10,
            language="en",
            author_safe="John Doe",
            embedded_metadata={"key": "value"},
        )
        assert metadata.page_count == 10
        assert metadata.language == "en"
        assert metadata.author_safe == "John Doe"
        assert metadata.embedded_metadata == {"key": "value"}

    def test_metadata_info_defaults(self):
        metadata = MetadataInfo()
        assert metadata.page_count is None
        assert metadata.language is None
        assert metadata.author_safe is None
        assert metadata.embedded_metadata == {}


class TestExtractionInfo:
    def test_create_extraction_info(self):
        extraction = ExtractionInfo(
            ocr_needed=True,
            ocr_used=True,
            tables_detected=True,
            signatures_detected=True,
            stamps_detected=True,
        )
        assert extraction.ocr_needed is True
        assert extraction.ocr_used is True
        assert extraction.tables_detected is True
        assert extraction.signatures_detected is True
        assert extraction.stamps_detected is True

    def test_extraction_info_defaults(self):
        extraction = ExtractionInfo()
        assert extraction.ocr_needed is False
        assert extraction.ocr_used is False
        assert extraction.tables_detected is False
        assert extraction.signatures_detected is False
        assert extraction.stamps_detected is False


class TestPrivacyInfo:
    def test_create_privacy_info(self):
        privacy = PrivacyInfo(
            pii_detected=True,
            pii_types=["email", "phone"],
            pii_count=5,
            masked_entities={"email": ["user@example.com"]},
        )
        assert privacy.pii_detected is True
        assert privacy.pii_types == ["email", "phone"]
        assert privacy.pii_count == 5
        assert privacy.masked_entities == {"email": ["user@example.com"]}

    def test_privacy_info_defaults(self):
        privacy = PrivacyInfo()
        assert privacy.pii_detected is False
        assert privacy.pii_types == []
        assert privacy.pii_count == 0
        assert privacy.masked_entities == {}


class TestClassificationInfo:
    def test_create_classification_info(self):
        classification = ClassificationInfo(
            label="document",
            confidence=0.95,
            source="ai",
        )
        assert classification.label == "document"
        assert classification.confidence == 0.95
        assert classification.source == "ai"

    def test_classification_info_defaults(self):
        classification = ClassificationInfo()
        assert classification.label == "unknown"
        assert classification.confidence == 0.0
        assert classification.source == "rules"


class TestDuplicateInfo:
    def test_create_duplicate_info(self):
        duplicate = DuplicateInfo(exact_duplicate=True)
        assert duplicate.exact_duplicate is True

    def test_duplicate_info_defaults(self):
        duplicate = DuplicateInfo()
        assert duplicate.exact_duplicate is False