# AGENTS.md

## Repository purpose
- DocuScope AI is a local-first document fingerprinting pipeline.
- The current codebase is a Python app rooted in `app/`, exposed via both a CLI (`python -m app.main`) and a local FastAPI demo (`uvicorn app.api.server:app`).
- `app/pipeline.py::run_pipeline` is the single shared orchestration entrypoint both surfaces call — do not duplicate scan/build/export logic elsewhere.

## Important directories
- `app/main.py`: thin CLI wrapper (argparse) around `app/pipeline.py`.
- `app/pipeline.py`: orchestration for scanning, parsing, sanitizing, classifying, exporting, and optional SQLite persistence. Shared by the CLI and the API.
- `app/scanner/`: recursive folder discovery for supported files.
- `app/security/`: resource-exhaustion guards (file size, zip-bomb, PDF page count, image decompression bomb) wired into the parsers and pipeline.
- `app/parsers/`: per-format parsing logic for PDF, DOCX, XLSX, TXT, and images.
- `app/privacy/`: PII detection, masking, and sanitization.
- `app/classify/`: rules-first classification, with a real Claude-backed AI fallback (`ai_classifier.py`) via `app/ai/`.
- `app/extract/`: regex-based extraction, with a real Claude-backed AI fallback (`ai_extractor.py`).
- `app/summarize/`: Claude-backed sanitized summary generation, with a deterministic template fallback.
- `app/ai/`: provider-agnostic AI layer. `provider.py` defines the interface + `get_provider()` choke point; `anthropic_provider.py` is the concrete Anthropic implementation; `prompts.py` holds the prompt-injection defense (untrusted-data framing); `schemas.py` holds Pydantic validation for model output, including a PII-leak check on summaries.
- `app/api/`: local FastAPI demo (`server.py`, `schemas.py`, `static/index.html`). No authentication — single-operator, localhost-only by design.
- `app/confidence/`: confidence and review scoring.
- `app/export/`: JSON and Excel output writers.
- `app/storage/`: optional SQLite persistence.
- `tests/`: pytest suite covering scanning, parsing, privacy, classification, confidence, fingerprint behavior, the AI layer (mocked, no live calls), resource guards, the pipeline, and the API routes.

## Setup and validation
- Create an environment with `python3.11 -m venv .venv && source .venv/bin/activate` (the project requires Python 3.11+; PEP 604 union syntax is used throughout).
- Install dependencies with `pip install -r requirements.txt`.
- Copy `.env.example` to `.env` and fill in `ANTHROPIC_API_KEY` to exercise the real AI fallback path; leaving it unset is fully supported and runs the deterministic-only path.
- Run tests with `pytest -q`. All AI-layer tests mock the Anthropic client — never add a test that makes a live API call.
- OCR-related behavior may require system packages such as `tesseract-ocr` and `poppler-utils`.

## Working conventions
- Prefer small, surgical changes.
- Keep privacy guarantees intact: do not bypass sanitization or introduce raw sensitive-data exports. The AI layer must never receive text that hasn't already passed through `app/privacy/sanitizer.py`.
- Preserve the existing rules-first / fallback-second flow unless the task explicitly changes it.
- Reuse the existing Pydantic models in `app/models/` instead of inventing parallel data shapes (see `app/ai/schemas.py` for an example: it validates directly into `ClassificationInfo` rather than a parallel type).
- The AI fallback modules (`ai_classifier.py`, `ai_extractor.py`, `ai_summarizer.py`) catch broad `Exception` around the provider call, by design — any AI-layer failure must degrade to the deterministic fallback, never crash or skip a document. Keep that pattern if you touch these files.
- Any new parser or file-format support should go through `app/security/resource_guards.py` before decompressing/decoding untrusted content.
- Add or update tests when behavior changes.

## Repository-specific notes
- `README.md` is kept in sync with actual behavior as of Phase 2 — no more Streamlit references; both the CLI and the FastAPI demo are real and functional.
- `requirements.txt` includes runtime and test dependencies together.
- `presidio-analyzer`/`presidio-anonymizer`/`spacy` were deliberately removed (were declared but unused) — see README's Roadmap for the deferred NER-based PII detection plan before re-adding them.

## Safe change checklist
- Confirm which file types and pipeline stages are affected.
- Verify output changes against both JSON/export behavior and fingerprint model expectations.
- If touching the AI layer, confirm the graceful-degradation path still works with `ANTHROPIC_API_KEY` unset.
- Run the smallest relevant pytest scope first, then `pytest -q` if needed.
- Avoid adding new dependencies unless required by the task.
