from __future__ import annotations

import re
from typing import Any


EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"(?:\+?\d[\d\-\s\(\)]{7,}\d)")
DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{2}/\d{2}/\d{4}\b")
MONEY_RE = re.compile(r"(?:CAD|USD|EUR|\$)\s?\d[\d,]*(?:\.\d{2})?", re.IGNORECASE)
ID_RE = re.compile(r"\b\d{6,}\b")


def detect_pii(text: str) -> dict[str, Any]:
    emails = sorted(set(EMAIL_RE.findall(text)))
    phones = sorted(set(PHONE_RE.findall(text)))
    dates = sorted(set(DATE_RE.findall(text)))
    money = sorted(set(MONEY_RE.findall(text)))
    ids = sorted(set(ID_RE.findall(text)))

    pii_types: list[str] = []
    if emails:
        pii_types.append("email")
    if phones:
        pii_types.append("phone")
    if ids:
        pii_types.append("id")
    if money:
        pii_types.append("financial")
    if dates:
        pii_types.append("date")

    return {
        "emails": emails,
        "phones": phones,
        "dates": dates,
        "money": money,
        "ids": ids,
        "pii_detected": len(pii_types) > 0,
        "pii_types": pii_types,
        "pii_count": len(emails) + len(phones) + len(ids) + len(money),
    }
