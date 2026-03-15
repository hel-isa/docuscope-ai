from __future__ import annotations


def classify_with_rules(text: str) -> dict:
    t = text.lower()

    if any(k in t for k in ["invoice", "amount due", "bill to", "invoice number"]):
        return {"label": "invoice", "confidence": 0.92, "source": "rules"}

    if any(k in t for k in ["receipt", "thank you for your purchase", "subtotal", "tax"]):
        return {"label": "receipt", "confidence": 0.88, "source": "rules"}

    if any(k in t for k in ["agreement", "effective date", "terms and conditions", "this contract"]):
        return {"label": "contract", "confidence": 0.86, "source": "rules"}

    if any(k in t for k in ["resume", "curriculum vitae", "experience", "education", "skills"]):
        return {"label": "resume", "confidence": 0.85, "source": "rules"}

    if any(k in t for k in ["statement period", "account number", "balance", "deposits", "withdrawals"]):
        return {"label": "bank_statement", "confidence": 0.84, "source": "rules"}

    if any(k in t for k in ["tax year", "notice of assessment", "t4", "w-2", "tax return"]):
        return {"label": "tax_document", "confidence": 0.82, "source": "rules"}

    if any(k in t for k in ["form", "please complete", "application form", "fields"]):
        return {"label": "form", "confidence": 0.75, "source": "rules"}

    if any(k in t for k in ["dear", "sincerely", "regards", "letter"]):
        return {"label": "letter", "confidence": 0.70, "source": "rules"}

    return {"label": "unknown", "confidence": 0.40, "source": "rules"}
