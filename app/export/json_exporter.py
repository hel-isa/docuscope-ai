from __future__ import annotations

import json
from pathlib import Path

from app.models.fingerprint import DocumentFingerprint


def export_fingerprint_json(fingerprint: DocumentFingerprint, output_dir: str | Path) -> Path:
    out_dir = Path(output_dir) / "json"
    out_dir.mkdir(parents=True, exist_ok=True)

    file_path = out_dir / f"{fingerprint.document_id}.json"
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(fingerprint.model_dump(mode="json"), f, indent=2, ensure_ascii=False)

    return file_path
