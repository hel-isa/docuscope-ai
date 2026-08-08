# AGENTS.md

## Repository purpose
- DocuScope AI is a local-first document fingerprinting pipeline.
- The current codebase is a Python CLI app rooted in `app/`.
- The main entrypoint is `python -m app.main`.

## Important directories
- `app/main.py`: orchestration for scanning, parsing, sanitizing, classifying, exporting, and optional SQLite persistence.
- `app/scanner/`: recursive folder discovery for supported files.
- `app/parsers/`: per-format parsing logic for PDF, DOCX, XLSX, TXT, and images.
- `app/privacy/`: PII detection, masking, and sanitization.
- `app/classify/`: rules-first classification with AI fallback placeholders.
- `app/extract/`: regex-based extraction with AI fallback placeholders.
- `app/confidence/`: confidence and review scoring.
- `app/export/`: JSON and Excel output writers.
- `app/storage/`: optional SQLite persistence.
- `tests/`: pytest suite covering scanning, parsing, privacy, classification, confidence, and fingerprint behavior.

## Setup and validation
- Create an environment with `python3 -m venv .venv && source .venv/bin/activate`.
- Install dependencies with `pip install -r requirements.txt`.
- Run tests with `pytest -q`.
- OCR-related behavior may require system packages such as `tesseract-ocr` and `poppler-utils`.

## Working conventions
- Prefer small, surgical changes.
- Keep privacy guarantees intact: do not bypass sanitization or introduce raw sensitive-data exports.
- Preserve the existing rules-first / fallback-second flow unless the task explicitly changes it.
- Reuse the existing Pydantic models in `app/models/` instead of inventing parallel data shapes.
- Add or update tests when behavior changes.

## Repository-specific notes
- `README.md` describes a future or broader architecture; verify actual behavior against code before changing anything.
- The checkout currently exposes the CLI pipeline; do not assume a Streamlit app exists unless you add it explicitly.
- `requirements.txt` includes runtime and test dependencies together.

## Safe change checklist
- Confirm which file types and pipeline stages are affected.
- Verify output changes against both JSON/export behavior and fingerprint model expectations.
- Run the smallest relevant pytest scope first, then `pytest -q` if needed.
- Avoid adding new dependencies unless required by the task.
