from __future__ import annotations

from typing import Any

from app.privacy.masker import mask_email, mask_id, mask_phone
from app.privacy.pii_detector import detect_pii


def sanitize_text(text: str) -> dict[str, Any]:
    pii = detect_pii(text)
    sanitized = text

    masked_entities = {
        "emails": [],
        "phones": [],
        "ids": [],
        "dates": pii["dates"],
        "money": pii["money"],
    }

    for email in pii["emails"]:
        masked = mask_email(email)
        sanitized = sanitized.replace(email, masked)
        masked_entities["emails"].append(masked)

    for phone in pii["phones"]:
        masked = mask_phone(phone)
        sanitized = sanitized.replace(phone, masked)
        masked_entities["phones"].append(masked)

    for identifier in pii["ids"]:
        masked = mask_id(identifier)
        sanitized = sanitized.replace(identifier, masked)
        masked_entities["ids"].append(masked)

    return {
        "sanitized_text": sanitized,
        "pii_detected": pii["pii_detected"],
        "pii_types": pii["pii_types"],
        "pii_count": pii["pii_count"],
        "masked_entities": masked_entities,
    }
