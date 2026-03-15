from app.privacy.masker import (
    mask_email,
    mask_id,
    mask_person_name,
    mask_phone,
    simplify_address,
)


def test_mask_email() -> None:
    assert mask_email("john.smith@gmail.com") == "j***@gmail.com"


def test_mask_phone() -> None:
    assert mask_phone("+1 514-555-1234").endswith("1234")


def test_mask_id() -> None:
    assert mask_id("123456789") == "*****6789"


def test_mask_person_name() -> None:
    assert mask_person_name("Antonio Ferreira") == "A****** F*******"


def test_simplify_address() -> None:
    assert simplify_address("123 Main St, Montreal, QC, Canada") == "QC, Canada"
