from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    try:
        return int(value)
    except ValueError as exc:
        # These values gate security-relevant limits (file size, page count,
        # AI retries/timeout) — fail fast and loud on a bad config rather
        # than silently falling back, which could mask a misconfiguration.
        raise ValueError(f"Invalid integer for environment variable {name}: {value!r}") from exc


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"Invalid number for environment variable {name}: {value!r}") from exc


APP_NAME = os.getenv("APP_NAME", "DocuScope AI")
PRIVACY_MODE = os.getenv("PRIVACY_MODE", "strict")
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./outputs"))

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".xlsx",
    ".txt",
    ".jpg",
    ".jpeg",
    ".png",
}

REVIEW_CONFIDENCE_THRESHOLD = _env_float("REVIEW_CONFIDENCE_THRESHOLD", 0.75)

# GenAI (Anthropic Claude) fallback layer.
AI_ENABLED = _env_bool("AI_ENABLED", True)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") or None
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
ANTHROPIC_TIMEOUT_SECONDS = _env_float("ANTHROPIC_TIMEOUT_SECONDS", 20.0)
ANTHROPIC_MAX_RETRIES = _env_int("ANTHROPIC_MAX_RETRIES", 2)

# AppSec: resource-exhaustion guards applied before/while parsing untrusted files.
MAX_FILE_SIZE_BYTES = _env_int("MAX_FILE_SIZE_BYTES", 50_000_000)
MAX_PDF_PAGES = _env_int("MAX_PDF_PAGES", 500)
MAX_ZIP_UNCOMPRESSED_BYTES = _env_int("MAX_ZIP_UNCOMPRESSED_BYTES", 200_000_000)
MAX_IMAGE_PIXELS = _env_int("MAX_IMAGE_PIXELS", 50_000_000)

# Local FastAPI demo: optional, off by default. When set, /scan rejects any
# input folder that resolves outside this root.
API_ALLOWED_ROOT = os.getenv("API_ALLOWED_ROOT") or None
