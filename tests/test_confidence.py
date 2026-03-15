from app.confidence.scoring import compute_confidence


def test_confidence_high_case() -> None:
    result = compute_confidence(
        classification_confidence=0.92,
        extraction_fields_count=4,
        ocr_used=False,
        text_length=500,
    )

    assert result["overall"] >= 0.75
    assert result["human_review_required"] is False


def test_confidence_low_case() -> None:
    result = compute_confidence(
        classification_confidence=0.40,
        extraction_fields_count=0,
        ocr_used=True,
        text_length=10,
    )

    assert result["overall"] < 0.75
    assert result["human_review_required"] is True
