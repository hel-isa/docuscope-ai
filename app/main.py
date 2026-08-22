from __future__ import annotations

import argparse
from pathlib import Path

from app.config import OUTPUT_DIR
from app.models.fingerprint import DocumentFingerprint
from app.pipeline import run_pipeline


def print_summary(fp: DocumentFingerprint) -> None:
    print("=" * 80)
    print(f"FILE: {fp.file_info.relative_path}")
    print(f"CLASS: {fp.classification.label} ({fp.classification.confidence})")
    print(f"LANGUAGE: {fp.metadata.language}")
    print(f"KEYWORDS: {fp.keywords[:5]}")
    print(f"PII: {fp.privacy.pii_detected} | TYPES: {fp.privacy.pii_types}")
    print(f"RISK FLAGS: {fp.risk.risk_flags}")
    print(f"REVIEW: {fp.review.human_review_required}")
    print(f"SUMMARY: {fp.sanitized_summary}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="DocuScope AI MVP")
    parser.add_argument("--input", required=True, help="Folder to scan")
    parser.add_argument("--output", default=str(OUTPUT_DIR), help="Output folder")
    parser.add_argument("--sqlite", action="store_true", help="Store results in SQLite")
    args = parser.parse_args()

    def print_scan_count(count: int) -> None:
        print(f"Found {count} supported files.\n")

    fingerprints = run_pipeline(
        args.input,
        args.output,
        use_sqlite=args.sqlite,
        on_result=print_summary,
        on_scan_complete=print_scan_count,
    )
    if fingerprints:
        # "document_report.xlsx" must match the filename export_fingerprints_excel
        # (app/export/excel_exporter.py) actually writes — run_pipeline doesn't
        # return the path, so this is a naming assumption, not a live lookup.
        print(f"Excel report: {Path(args.output) / 'document_report.xlsx'}")


if __name__ == "__main__":
    main()
