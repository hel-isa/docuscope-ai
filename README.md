# DocuScope AI

[![Tests](https://github.com/hel-isa/docuscope-ai/actions/workflows/tests.yml/badge.svg)](...)
[![Security Scanning](https://github.com/hel-isa/docuscope-ai/actions/workflows/security.yml/badge.svg)](...)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()

**Privacy-first hybrid AI document fingerprinting**

DocuScope AI is a local-first document intelligence project that scans folders and subfolders, processes multiple file types, extracts useful document signals, masks sensitive data, and generates **sanitized document fingerprints** for reporting and review.

---

## Why this project exists

DocuScope AI started from a personal need: I wanted a way to search through my own files and quickly find specific information without manually opening and reviewing every document one by one.

It also serves as a practical learning project to help me understand how AI can be integrated into software in a useful, structured, and privacy-conscious way — and to practice building it the way an AppSec-minded engineer would: threat model the AI layer explicitly, guard against malicious/adversarial input, and never let an optional enhancement (AI) compromise the reliability or privacy guarantees of the deterministic core.

---

## Project status

**Phase 1** built the deterministic MVP foundation: folder scanning, parser integration, OCR support, privacy-aware sanitization, rules-based classification, structured export, and automated testing.

**Phase 2** replaced the AI placeholders with a real, provider-abstracted Anthropic Claude integration, added concrete resource-exhaustion guards against malicious/adversarial documents, and added a local FastAPI demo UI. See [Roadmap](#roadmap) for what's next.

---

## Current architecture

```text
Selected Folder
   -> File Scanner
   -> Resource Guards (size / zip-bomb / page-count / pixel-count limits)
   -> Parser / OCR
   -> Privacy Redaction Layer
   -> AI Enrichment Layer (rules-first, Claude fallback on sanitized text only)
        - rules + AI classification
        - rules + AI extraction
        - AI sanitized summary (PII-checked before use)
   -> Confidence + Review Flag
   -> JSON + Excel Report
   -> Optional SQLite
````

---

## Scope

### Included

* recursive folder scanning
* support for:

  * PDF
  * DOCX
  * XLSX
  * TXT
  * JPG
  * PNG
* PDF text extraction
* OCR for images
* OCR fallback for scanned PDFs
* file metadata extraction
* privacy masking and sanitization
* rules-based classification, with a real Claude-backed AI fallback
* structured extraction, with a real Claude-backed AI fallback
* AI-generated sanitized summaries, with a deterministic template fallback
* confidence scoring
* review flagging
* resource-exhaustion guards (oversized files, zip bombs, PDF page-count bombs, image decompression bombs)
* JSON export
* Excel export
* optional SQLite persistence
* local FastAPI demo app
* automated tests (including adversarial/security-focused fixtures)

### Not included yet

* NER-based PII detection (names, addresses, free-text PII) — current detection is pattern/regex-based; see [Roadmap](#roadmap)
* semantic near-duplicate detection
* advanced signature/stamp detection
* enterprise-grade access controls / API authentication
* production deployment
* packaged macOS desktop app

---

## Core principles

### Privacy first

DocuScope AI is designed to avoid exposing sensitive data unnecessarily.

* sensitive values are masked **before** anything (rules, AI, exports) sees the text
* the AI fallback layer only ever receives already-sanitized text — raw document content never leaves the deterministic pipeline
* AI-generated output is itself re-checked for PII-shaped content before being used, verifying that redaction actually held
* outputs are sanitized
* the project remains local-first by design

### Hybrid AI design

The system separates:

* deterministic software engineering tasks (rules-based classification, regex extraction, template summaries)
* AI-powered interpretation tasks (an Anthropic Claude fallback, used only when the deterministic path is low-confidence or empty)

The AI layer sits behind a small provider-agnostic interface (`app/ai/provider.py`), so it degrades to the deterministic logic automatically whenever no API key is configured or a call fails — the pipeline never depends on AI to function.

### Local-first MVP

The project is intentionally built to run locally:

* easier to debug
* lower cost
* better privacy control
* ideal for learning and portfolio development

---

## Supported file types

* `.pdf`
* `.docx`
* `.xlsx`
* `.txt`
* `.jpg`
* `.jpeg`
* `.png`

---

## Current document classes

Rules-first classification (with an AI fallback) supports:

* `invoice`
* `receipt`
* `contract`
* `resume`
* `bank_statement`
* `tax_document`
* `form`
* `letter`
* `unknown`

---

## What the app does

For each supported file, DocuScope AI currently:

1. scans the selected folder recursively
2. identifies supported documents
3. rejects files that trip a resource-exhaustion guard (oversized, zip-bomb-shaped, too many PDF pages, decompression-bomb image)
4. extracts file metadata
5. parses text/content
6. applies OCR when needed
7. detects basic sensitive data patterns
8. masks sensitive values
9. classifies the document (rules first, Claude fallback if low-confidence)
10. extracts structured fields (regex first, Claude fallback if empty)
11. generates a sanitized fingerprint and summary
12. computes confidence and review status
13. exports results to JSON, Excel, and optionally SQLite

---

## Privacy model

DocuScope AI is built to generate **sanitized fingerprints**, not raw document dumps.

Examples of privacy-safe behavior:

* emails, phone numbers, and IDs are masked before any downstream processing
* the AI fallback layer never receives raw/unmasked text
* AI output is validated against a schema and re-scanned for PII-shaped content before use
* summaries are sanitized
* reports are intended for structured review, not raw content exposure

See [SECURITY.md](SECURITY.md) for the full threat model, including prompt-injection and resource-exhaustion mitigations.

---

## Project structure

```text
docuscope-ai/
│
├── app/
│   ├── main.py                # thin CLI entrypoint
│   ├── pipeline.py            # shared orchestration (scan -> fingerprint -> export), used by CLI and API
│   ├── config.py              # env-driven settings (.env)
│   ├── models/
│   │   └── fingerprint.py
│   ├── scanner/
│   │   └── folder_scanner.py
│   ├── security/
│   │   └── resource_guards.py # zip-bomb / page-count / pixel-count / file-size guards
│   ├── parsers/
│   │   ├── pdf_parser.py
│   │   ├── docx_parser.py
│   │   ├── xlsx_parser.py
│   │   ├── txt_parser.py
│   │   └── image_parser.py
│   ├── ocr/
│   │   └── ocr_service.py
│   ├── privacy/
│   │   ├── pii_detector.py
│   │   ├── masker.py
│   │   └── sanitizer.py
│   ├── classify/
│   │   ├── rules_classifier.py
│   │   ├── ai_classifier.py
│   │   └── constants.py
│   ├── extract/
│   │   ├── regex_extractors.py
│   │   └── ai_extractor.py
│   ├── summarize/
│   │   └── ai_summarizer.py
│   ├── ai/                    # provider-agnostic AI layer (Anthropic Claude implementation)
│   │   ├── provider.py
│   │   ├── anthropic_provider.py
│   │   ├── prompts.py
│   │   └── schemas.py
│   ├── api/                   # local FastAPI demo
│   │   ├── server.py
│   │   ├── schemas.py
│   │   └── static/index.html
│   ├── confidence/
│   │   └── scoring.py
│   ├── export/
│   │   ├── json_exporter.py
│   │   └── excel_exporter.py
│   ├── storage/
│   │   └── sqlite_store.py
│   └── utils/
│       └── text_utils.py
│
├── outputs/
├── tests/
├── .env.example
├── requirements.txt
├── pytest.ini
└── README.md
```

---

## Installation

### 1. Create a virtual environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Install OCR dependencies

#### macOS

```bash
brew install tesseract
brew install poppler
```

#### Ubuntu / Codespaces

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr poppler-utils
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Fill in `ANTHROPIC_API_KEY` to enable the real Claude fallback layer. Leaving it empty is fully supported — the pipeline runs entirely on the deterministic rules/regex/template logic, with zero external calls and zero cost.

---

## Run locally (CLI)

```bash
python -m app.main --input "/path/to/folder" --output "./outputs" --sqlite
```

### Parameters

* `--input` → folder to scan
* `--output` → output folder
* `--sqlite` → save sanitized results into SQLite

---

## Run locally (browser demo)

DocuScope AI includes a minimal local FastAPI demo.

```bash
uvicorn app.api.server:app --reload
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000) to:

* enter a folder path
* run a scan
* view sanitized results (classification, PII flags, summary, review status)

This is a **local, single-operator demo tool** — no authentication is included, and it should not be exposed to a network. See [SECURITY.md](SECURITY.md) for details.

---

## Outputs

### JSON

One sanitized JSON fingerprint per processed document.

### Excel

A flattened report of processed documents.

### SQLite

Optional sanitized record storage for local querying.

---

## Tests

Run all tests:

```bash
pytest -q
```

Run verbose tests:

```bash
pytest -v
```

The suite includes adversarial/security-focused fixtures (zip-bomb-shaped DOCX/XLSX, PDF page-count bombs, image decompression bombs, and a simulated prompt-injection payload) alongside the functional tests. All AI-layer tests mock the Anthropic client — no live API calls are made in CI.

---

## Current limitations

* NER-based PII detection (names, addresses, free-text PII) is not yet implemented — detection today is pattern/regex-based
* duplicate detection is exact-hash only
* language detection is heuristic
* signature/stamp detection is not fully implemented
* the FastAPI demo has no authentication (by design, for a local single-operator tool)
* no production deployment yet
* no packaged macOS desktop app yet

---

## Roadmap

### Phase 3

* NER-based PII detection (Presidio + spaCy), as an opt-in layer alongside the existing regex detector
* improve duplicate detection (semantic near-duplicate, not just exact-hash)
* improve structured extraction
* improve review workflow

### Phase 4

* improve local UI
* package for macOS
* harden for production scenarios (auth, deployment)

## Author

**He-Isa**

DocuScope AI — Privacy-first hybrid AI document fingerprinting
