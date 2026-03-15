from __future__ import annotations


def generate_sanitized_summary(sanitized_text: str, doc_class: str) -> str:
    text = " ".join(sanitized_text.split())

    if doc_class == "invoice":
        return "Invoice-like document containing dates, references, and financial information."

    if doc_class == "receipt":
        return "Receipt-like document containing merchant and purchase-related financial details."

    if doc_class == "contract":
        return "Contract-like document containing agreement terms, parties, and effective date information."

    if doc_class == "resume":
        return "Resume-like document containing work experience, education, and skills information."

    if doc_class == "bank_statement":
        return "Bank statement-like document containing account and balance-related financial information."

    if doc_class == "tax_document":
        return "Tax-related document containing year and financial reporting information."

    if doc_class == "form":
        return "Form-like document containing fields to complete and structured information."

    if doc_class == "letter":
        return "Letter-like document containing written correspondence."

    if not text:
        return "No readable content extracted."

    return text[:220] + ("..." if len(text) > 220 else "")
