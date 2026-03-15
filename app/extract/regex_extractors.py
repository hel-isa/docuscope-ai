from __future__ import annotations

import re
from typing import Any


def extract_fields_by_regex(text: str, doc_class: str) -> dict[str, Any]:
    fields: dict[str, Any] = {}

    invoice_number = re.search(r"(?:invoice(?:\s*#|\s*number)?[:\s-]*)([A-Z0-9\-]+)", text, re.IGNORECASE)
    contract_number = re.search(r"(?:contract(?:\s*#|\s*number)?[:\s-]*)([A-Z0-9\-]+)", text, re.IGNORECASE)
    date_match = re.search(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{2}/\d{2}/\d{4}\b", text)
    money_matches = re.findall(r"(?:CAD|USD|EUR|\$)\s?\d[\d,]*(?:\.\d{2})?", text, re.IGNORECASE)

    if doc_class == "invoice":
        if invoice_number:
            fields["invoice_number"] = invoice_number.group(1)
        if date_match:
            fields["invoice_date"] = date_match.group(0)
        if money_matches:
            fields["total"] = money_matches[-1]

    if doc_class == "contract":
        if contract_number:
            fields["contract_number"] = contract_number.group(1)
        if date_match:
            fields["effective_date"] = date_match.group(0)

    if doc_class == "receipt":
        if date_match:
            fields["purchase_date"] = date_match.group(0)
        if money_matches:
            fields["total"] = money_matches[-1]

    if doc_class == "bank_statement":
        if date_match:
            fields["statement_period"] = date_match.group(0)
        if "balance" in text.lower():
            fields["balance_present"] = True

    if doc_class == "resume":
        fields["education_present"] = "education" in text.lower()
        fields["experience_present"] = "experience" in text.lower()
        if "skills" in text.lower():
            fields["skills_present"] = True

    return fields
