from __future__ import annotations

import re


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_keywords(text: str, top_n: int = 10) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9\-]{2,}", text.lower())

    stop_words = {
        "the", "and", "for", "with", "this", "that", "from", "have", "will",
        "your", "you", "are", "not", "but", "all", "can", "use", "into",
        "les", "des", "une", "pour", "avec", "dans", "sur", "pas", "est",
        "invoice", "page", "document"
    }

    freq: dict[str, int] = {}
    for word in words:
        if word not in stop_words:
            freq[word] = freq.get(word, 0) + 1

    sorted_words = sorted(freq.items(), key=lambda item: item[1], reverse=True)
    return [word for word, _ in sorted_words[:top_n]]


def guess_language(text: str) -> str | None:
    sample = text.lower()

    if not sample.strip():
        return None

    french_markers = [" le ", " la ", " les ", " une ", " des ", " bonjour ", " merci "]
    portuguese_markers = [" o ", " a ", " os ", " as ", " obrigado ", " para ", " você "]

    french_score = sum(marker in f" {sample} " for marker in french_markers)
    portuguese_score = sum(marker in f" {sample} " for marker in portuguese_markers)

    if french_score > portuguese_score and french_score > 0:
        return "fr"

    if portuguese_score > french_score and portuguese_score > 0:
        return "pt"

    return "en"


def make_text_preview(text: str, max_length: int = 300) -> str:
    normalized = normalize_whitespace(text)
    if len(normalized) <= max_length:
        return normalized
    return normalized[:max_length] + "..."
