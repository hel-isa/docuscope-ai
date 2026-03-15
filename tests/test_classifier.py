from app.classify.rules_classifier import classify_with_rules


def test_classify_invoice() -> None:
    text = "Invoice number INV-123 amount due CAD 120.00 bill to customer"
    result = classify_with_rules(text)

    assert result["label"] == "invoice"
    assert result["confidence"] >= 0.8


def test_classify_resume() -> None:
    text = "Resume with experience education and skills in python and cloud"
    result = classify_with_rules(text)

    assert result["label"] == "resume"


def test_classify_unknown() -> None:
    text = "random words without known structure"
    result = classify_with_rules(text)

    assert result["label"] == "unknown"
