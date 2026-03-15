from __future__ import annotations

from pathlib import Path


APP_NAME = "DocuScope AI"
PRIVACY_MODE = "strict"
OUTPUT_DIR = Path("./outputs")

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".xlsx",
    ".txt",
    ".jpg",
    ".jpeg",
    ".png",
}

REVIEW_CONFIDENCE_THRESHOLD = 0.75
