from __future__ import annotations

import argparse
import hashlib
import mimetypes
from datetime import datetime
from pathlib import Path

from app.config import OUTPUT_DIR
from app.classify.ai_classifier import classify_with_ai_fallback
from app.classify.rules_classifier import classify_with_rules
from app.confidence.scoring import compute_confidence
from app.export.excel_exporter import export_fingerprints_excel
from app.export.json_exporter import export_fingerprint_json
from app.extract.ai_extractor import extract_fields_with_ai_fallback
from app.extract.regex_extractors import extract_fields_by_regex
from app.models.fingerprint import (
    ClassificationInfo,
    ConfidenceInfo,
    DocumentFingerprint,
    ExtractionInfo,
    FileInfo,
    MetadataInfo,
    PrivacyInfo,
    ReviewInfo,
)
from app.parsers.docx_parser import parse_docx
from app.parsers.image_parser import parse_image
from app.parsers.pdf_parser import parse_pdf
from app.parsers.txt_parser import parse_txt
from app.parsers.xlsx_parser import parse_xlsx
from app.privacy.sanitizer import sanitize_text
from app.scanner.folder_scanner import scan_folder
from app.storage.sqlite_store import init_db, save_fingerprint
from app.summarize.ai_summarizer import generate_sanitized_summary
from app.utils.text_utils import extract_keywords, guess_language


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def guess_mime(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    return mime or "application/octet-stream"


def parse_file(file_path: Path) -> dict:
    ext = file_path.suffix.lower()

    if ext == ".pdf":
        return parse_pdf(file_path)
    if ext == ".txt":
        return parse_txt(file_path)
    if ext == ".docx":
        return parse_docx(file_path)
    if ext == ".xlsx":
        return parse_xlsx(file_path)
    if ext in {".jpg", ".jpeg", ".png"}:
        return parse_image(file_path)

    raise ValueError(f"Unsupported extension: {ext}")


def build_fingerprint(file_path: Path, seen_hashes: dict[str, str]) -> DocumentFingerprint:
    stat = file_path.stat()
    file_hash = sha256_file(file_path)
    parse_result = parse_file(file_path)

    raw_text = parse_result["text"]
    sanitized = sanitize_text(raw_text)
    sanitized_text = sanitized["sanitized_text"]

    classification = classify_with_rules(sanitized_text)

    if classification["label"] == "unknown" or classification["confidence"] < 0.75:
        classification = classify_with_ai_fallback(sanitized_text)

    extracted_fields = extract_fields_by_regex(sanitized_text, classification["label"])
    if not extracted_fields:
        extracted_fields = extract_fields_with_ai_fallback(sanitized_text, classification["label"])

    summary = generate_sanitized_summary(sanitized_text, classification["label"])
    keywords = extract_keywords(sanitized_text)
    language = guess_language(sanitized_text)

    scores = compute_confidence(
        classification_confidence=classification["confidence"],
        extraction_fields_count=len(extracted_fields),
        ocr_used=parse_result["ocr_used"],
        text_length=len(raw_text),
    )

    exact_duplicate = file_hash in seen_hashes
    exact_duplicate_of = seen_hashes.get(file_hash)
    if not exact_duplicate:
        seen_hashes[file_hash] = str(file_path)

    risk_flags = []
    if sanitized["pii_detected"]:
        risk_flags.append("contains_pii")
    if classification["label"] in {"invoice", "receipt", "bank_statement", "tax_document"}:
        risk_flags.append("contains_financial_data")
    if classification["label"] == "unknown":
        risk_flags.append("unknown_document_type")
    if parse_result["ocr_needed"] and not parse_result["ocr_used"]:
        risk_flags.append("ocr_recommended")
    if exact_duplicate:
        risk_flags.append("duplicate_file")

    fingerprint = DocumentFingerprint(
        file_info=FileInfo(
            file_name=file_path.name,
            full_path=str(file_path.resolve()),
            file_extension=file_path.suffix.lower(),
            mime_type=guess_mime(file_path),
            file_size_bytes=stat.st_size,
            created_at_fs=datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
            modified_at_fs=datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            sha256_hash=file_hash,
        ),
        metadata=MetadataInfo(
            page_count=parse_result["page_count"],
            language=language,
            author_safe=parse_result["author_safe"],
            embedded_metadata=parse_result["embedded_metadata"],
        ),
        extraction=ExtractionInfo(
            ocr_needed=parse_result["ocr_needed"],
            ocr_used=parse_result["ocr_used"],
            tables_detected=parse_result["tables_detected"],
            signatures_detected=parse_result["signatures_detected"],
            stamps_detected=parse_result["stamps_detected"],
        ),
        privacy=PrivacyInfo(
            pii_detected=sanitized["pii_detected"],
            pii_types=sanitized["pii_types"],
            pii_count=sanitized["pii_count"],
            masked_entities=sanitized["masked_entities"],
        ),
        classification=ClassificationInfo(
            label=classification["label"],
            confidence=classification["confidence"],
            source=classification["source"],
        ),
        sanitized_summary=summary,
        document_specific_fields=extracted_fields,
        keywords=keywords,
        title_sanitized=file_path.stem,
        parse_status="success",
    )

    fingerprint.duplicate.exact_duplicate = exact_duplicate
    fingerprint.duplicate.exact_duplicate_of = exact_duplicate_of
    fingerprint.risk.risk_flags = risk_flags
    fingerprint.confidence = ConfidenceInfo(
        overall=scores["overall"],
        classification=scores["classification"],
        extraction=scores["extraction"],
        ocr=scores["ocr"],
    )
    fingerprint.review = ReviewInfo(
        human_review_required=scores["human_review_required"],
        reason=scores["reason"],
    )

    return fingerprint


def main() -> None:
    parser = argparse.ArgumentParser(description="DocuScope AI MVP")
    parser.add_argument("--input", required=True, help="Folder to scan")
    parser.add_argument("--output", default=str(OUTPUT_DIR), help="Output folder")
    parser.add_argument("--sqlite", action="store_true", help="Store results in SQLite")
    args = parser.parse_args()

    files = scan_folder(args.input)
    print(f"Found {len(files)} supported files.\n")

    seen_hashes: dict[str, str] = {}
    fingerprints: list[DocumentFingerprint] = []

    db_path = Path(args.output) / "docuscope_ai.db"
    if args.sqlite:
        Path(args.output).mkdir(parents=True, exist_ok=True)
        init_db(db_path)

    for file_path in files:
        try:
            fp = build_fingerprint(file_path, seen_hashes)
            fingerprints.append(fp)
            export_fingerprint_json(fp, args.output)
            if args.sqlite:
                save_fingerprint(db_path, fp)

            print("=" * 80)
            print(f"FILE: {fp.file_info.full_path}")
            print(f"CLASS: {fp.classification.label} ({fp.classification.confidence})")
            print(f"LANGUAGE: {fp.metadata.language}")
            print(f"KEYWORDS: {fp.keywords[:5]}")
            print(f"PII: {fp.privacy.pii_detected} | TYPES: {fp.privacy.pii_types}")
            print(f"RISK FLAGS: {fp.risk.risk_flags}")
            print(f"REVIEW: {fp.review.human_review_required}")
            print(f"SUMMARY: {fp.sanitized_summary}\n")
        except Exception as exc:
            print("=" * 80)
            print(f"FAILED: {file_path}")
            print(f"ERROR: {exc}\n")

    if fingerprints:
        report_path = export_fingerprints_excel(fingerprints, args.output)
        print(f"Excel report: {report_path}")


if __name__ == "__main__":
    main()
