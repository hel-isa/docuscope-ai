from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from app.models.fingerprint import DocumentFingerprint


def init_db(db_path: str | Path) -> None:
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            document_id TEXT PRIMARY KEY,
            file_name TEXT,
            full_path TEXT,
            file_extension TEXT,
            sha256_hash TEXT,
            classification_label TEXT,
            classification_confidence REAL,
            overall_confidence REAL,
            pii_detected INTEGER,
            pii_types_json TEXT,
            sanitized_summary TEXT,
            parse_status TEXT,
            fingerprint_json TEXT
        )
        """
    )

    conn.commit()
    conn.close()


def save_fingerprint(db_path: str | Path, fingerprint: DocumentFingerprint) -> None:
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    cur.execute(
        """
        INSERT OR REPLACE INTO documents (
            document_id,
            file_name,
            full_path,
            file_extension,
            sha256_hash,
            classification_label,
            classification_confidence,
            overall_confidence,
            pii_detected,
            pii_types_json,
            sanitized_summary,
            parse_status,
            fingerprint_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            fingerprint.document_id,
            fingerprint.file_info.file_name,
            fingerprint.file_info.full_path,
            fingerprint.file_info.file_extension,
            fingerprint.file_info.sha256_hash,
            fingerprint.classification.label,
            fingerprint.classification.confidence,
            fingerprint.confidence.overall,
            int(fingerprint.privacy.pii_detected),
            json.dumps(fingerprint.privacy.pii_types, ensure_ascii=False),
            fingerprint.sanitized_summary,
            fingerprint.parse_status,
            json.dumps(fingerprint.model_dump(mode="json"), ensure_ascii=False),
        ),
    )

    conn.commit()
    conn.close()
