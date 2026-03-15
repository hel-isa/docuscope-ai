from __future__ import annotations

from app.config import REVIEW_CONFIDENCE_THRESHOLD


def compute_confidence(
    classification_confidence: float,
    extraction_fields_count: int,
    ocr_used: bool,
    text_length: int,
) -> dict:
    extraction_confidence = min(1.0, 0.4 + (0.1 * extraction_fields_count))
    ocr_confidence = 0.70 if ocr_used else 0.95

    if text_length < 40:
        ocr_confidence -= 0.20
        extraction_confidence -= 0.15

    overall = round(
        (classification_confidence * 0.4)
        + (max(extraction_confidence, 0.0) * 0.3)
        + (max(ocr_confidence, 0.0) * 0.2)
        + (0.9 * 0.1),
        3
    )

    review_required = overall < REVIEW_CONFIDENCE_THRESHOLD

    return {
        "overall": overall,
        "classification": classification_confidence,
        "extraction": round(max(extraction_confidence, 0.0), 3),
        "ocr": round(max(ocr_confidence, 0.0), 3),
        "human_review_required": review_required,
        "reason": "low_confidence" if review_required else None,
    }
