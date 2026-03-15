from app.privacy.sanitizer import sanitize_text


def test_sanitize_text_masks_email_phone_and_id() -> None:
    text = "Contact me at john.smith@gmail.com or +1 514-555-1234. ID 123456789."
    result = sanitize_text(text)

    assert result["pii_detected"] is True
    assert "email" in result["pii_types"]
    assert "phone" in result["pii_types"]
    assert "id" in result["pii_types"]

    sanitized = result["sanitized_text"]
    assert "john.smith@gmail.com" not in sanitized
    assert "123456789" not in sanitized
    assert "j***@gmail.com" in sanitized
