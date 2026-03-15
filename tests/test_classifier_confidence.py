from app.classify.rules_classifier import classify_with_rules
from app.confidence.scoring import compute_confidence


def test_classify_with_rules_hits_known_labels() -> None:
    assert classify_with_rules("Invoice number: INV-001") == {
        "label": "invoice",
        "confidence": 0.92,
        "source": "rules",
    }

    assert classify_with_rules("Thank you for your purchase and subtotal") == {
        "label": "receipt",
        "confidence": 0.88,
        "source": "rules",
    }

    assert classify_with_rules("Random text with no keywords")["label"] == "unknown"


def test_compute_confidence_high_signal_no_review() -> None:
    out = compute_confidence(
        classification_confidence=0.92,
        extraction_fields_count=4,
        ocr_used=False,
        text_length=500,
    )

    assert out["overall"] >= 0.75
    assert out["human_review_required"] is False
    assert out["reason"] is None


def test_compute_confidence_low_signal_requires_review() -> None:
    out = compute_confidence(
        classification_confidence=0.40,
        extraction_fields_count=0,
        ocr_used=True,
        text_length=20,
    )

    assert out["overall"] < 0.75
    assert out["human_review_required"] is True
    assert out["reason"] == "low_confidence"
    assert out["ocr"] == 0.5
    assert out["extraction"] == 0.25
