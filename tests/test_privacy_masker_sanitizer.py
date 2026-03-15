from app.privacy.masker import mask_email, mask_id, mask_person_name, mask_phone, simplify_address
from app.privacy.pii_detector import detect_pii
from app.privacy.sanitizer import sanitize_text


def test_mask_email_variants() -> None:
    assert mask_email("john.smith@gmail.com") == "j***@gmail.com"
    assert mask_email("@example.com") == "***@example.com"
    assert mask_email("not-an-email") == "***"


def test_mask_phone_variants() -> None:
    assert mask_phone("+1 514-555-1234") == "+1 ***-***-1234"
    assert mask_phone("514-555-9999") == "***-***-9999"
    assert mask_phone("12") == "***"


def test_mask_id_and_name_and_address() -> None:
    assert mask_id("123456789") == "*****6789"
    assert mask_id("123", visible_last=4) == "***"

    assert mask_person_name("Antonio Ferreira") == "A****** F*******"
    assert mask_person_name("A") == "*"

    assert simplify_address("123 Main St, Montreal, QC, Canada") == "QC, Canada"
    assert simplify_address("Single block") == "Single block"
    assert simplify_address("   ") == "***"


def test_detect_pii_finds_expected_types_and_count() -> None:
    text = (
        "Contact jane.doe@example.com or +1 514-555-1234 on 2026-03-15. "
        "Invoice total: USD 999.00. Customer ID 123456."
    )
    result = detect_pii(text)

    assert result["pii_detected"] is True
    assert set(result["pii_types"]) == {"email", "phone", "id", "financial", "date"}
    assert "jane.doe@example.com" in result["emails"]
    assert "+1 514-555-1234" in result["phones"]
    assert "123456" in result["ids"]
    assert "USD 999.00" in result["money"]
    assert result["pii_count"] >= 4


def test_sanitize_text_masks_detected_entities() -> None:
    raw = "Email: jane.doe@example.com | Phone: 514-555-1234 | ID: 123456789"

    out = sanitize_text(raw)

    assert out["pii_detected"] is True
    assert out["pii_count"] >= 3

    sanitized = out["sanitized_text"]
    assert "j***@example.com" in sanitized
    assert "***-***-1234" in sanitized
    assert "6789" in sanitized

    assert out["masked_entities"]["emails"] == ["j***@example.com"]
    assert "***-***-1234" in out["masked_entities"]["phones"]
    assert out["masked_entities"]["ids"]
