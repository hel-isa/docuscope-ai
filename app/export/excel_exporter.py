from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from app.models.fingerprint import DocumentFingerprint


def flatten_fingerprint(f: DocumentFingerprint) -> dict:
    return {
        "document_id": f.document_id,
        "file_name": f.file_info.file_name,
        "full_path": f.file_info.full_path,
        "file_extension": f.file_info.file_extension,
        "mime_type": f.file_info.mime_type,
        "file_size_bytes": f.file_info.file_size_bytes,
        "created_at_fs": f.file_info.created_at_fs,
        "modified_at_fs": f.file_info.modified_at_fs,
        "sha256_hash": f.file_info.sha256_hash,
        "page_count": f.metadata.page_count,
        "language": f.metadata.language,
        "author_safe": f.metadata.author_safe,
        "ocr_needed": f.extraction.ocr_needed,
        "ocr_used": f.extraction.ocr_used,
        "tables_detected": f.extraction.tables_detected,
        "signatures_detected": f.extraction.signatures_detected,
        "classification_label": f.classification.label,
        "classification_confidence": f.classification.confidence,
        "classification_source": f.classification.source,
        "overall_confidence": f.confidence.overall,
        "pii_detected": f.privacy.pii_detected,
        "pii_types_json": json.dumps(f.privacy.pii_types, ensure_ascii=False),
        "pii_count": f.privacy.pii_count,
        "masked_entities_json": json.dumps(f.privacy.masked_entities, ensure_ascii=False),
        "title_sanitized": f.title_sanitized,
        "sanitized_summary": f.sanitized_summary,
        "keywords_json": json.dumps(f.keywords, ensure_ascii=False),
        "document_specific_fields_json": json.dumps(f.document_specific_fields, ensure_ascii=False),
        "exact_duplicate": f.duplicate.exact_duplicate,
        "exact_duplicate_of": f.duplicate.exact_duplicate_of,
        "risk_flags_json": json.dumps(f.risk.risk_flags, ensure_ascii=False),
        "anomaly_flags_json": json.dumps(f.risk.anomaly_flags, ensure_ascii=False),
        "human_review_required": f.review.human_review_required,
        "review_reason": f.review.reason,
        "parse_status": f.parse_status,
        "error_message_safe": f.error_message_safe,
    }


def export_fingerprints_excel(fingerprints: list[DocumentFingerprint], output_dir: str | Path) -> Path:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = [flatten_fingerprint(f) for f in fingerprints]
    df = pd.DataFrame(rows)

    file_path = out_dir / "document_report.xlsx"
    df.to_excel(file_path, index=False)

    return file_path
