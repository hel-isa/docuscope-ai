from __future__ import annotations

import re


def mask_email(email: str) -> str:
    """
    Example:
    john.smith@gmail.com -> j***@gmail.com
    """
    email = email.strip()
    if "@" not in email:
        return "***"

    local_part, domain = email.split("@", 1)

    if not local_part:
        return f"***@{domain}"

    return f"{local_part[0]}***@{domain}"


def mask_phone(phone: str) -> str:
    """
    Example:
    +1 514-555-1234 -> +1 ***-***-1234
    Keeps only the last 4 digits visible.
    """
    digits = re.sub(r"\D", "", phone)

    if len(digits) < 4:
        return "***"

    last4 = digits[-4:]
    if phone.strip().startswith("+"):
        country = "+" + digits[:-10] if len(digits) > 10 else "+"
        return f"{country} ***-***-{last4}"

    return f"***-***-{last4}"


def mask_id(value: str, visible_last: int = 4) -> str:
    """
    Example:
    123456789 -> *****6789
    """
    cleaned = value.strip()
    if len(cleaned) <= visible_last:
        return "*" * len(cleaned)

    hidden_part = "*" * (len(cleaned) - visible_last)
    return f"{hidden_part}{cleaned[-visible_last:]}"


def mask_person_name(name: str) -> str:
    """
    Example:
    Antonio Ferreira -> A****** F*******
    """
    parts = [part for part in name.strip().split() if part]
    if not parts:
        return "***"

    masked_parts = []
    for part in parts:
        if len(part) == 1:
            masked_parts.append("*")
        else:
            masked_parts.append(part[0] + "*" * (len(part) - 1))

    return " ".join(masked_parts)


def simplify_address(address: str) -> str:
    """
    Very simple MVP placeholder.
    Tries to reduce precision by keeping only the last 2 comma-separated parts.

    Example:
    123 Main St, Montreal, QC, Canada -> QC, Canada
    125 King St W, Toronto, ON -> Toronto, ON
    """
    parts = [part.strip() for part in address.split(",") if part.strip()]
    if len(parts) >= 2:
        return ", ".join(parts[-2:])
    if parts:
        return parts[0]
    return "***"
