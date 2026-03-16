# DocuScope AI

**Privacy-first hybrid AI document fingerprinting**

DocuScope AI is a local-first document intelligence project that scans folders and subfolders, processes multiple file types, extracts useful document signals, masks sensitive data, and generates **sanitized document fingerprints** for reporting and review.

---

## Why this project exists

DocuScope AI started from a personal need: I wanted a way to search through my own files and quickly find specific information without manually opening and reviewing every document one by one.

It also serves as a practical learning project to help me understand how AI can be integrated into software in a useful, structured, and privacy-conscious way. Instead of building a purely theoretical prototype, I wanted to create a real application that combines document parsing, OCR, privacy masking, classification, structured reporting, and a future path toward hybrid AI enrichment.

---

## Phase 1 objective

Phase 1 establishes the MVP foundation of DocuScope AI.

The objective of this phase is to build the core pipeline required to process documents locally and safely before introducing real AI capabilities in later phases. This includes folder scanning, parser integration, OCR support, privacy-aware sanitization, rules-based classification, structured export, validation, and automated testing.

Phase 1 is focused on **foundation and reliability**, not advanced AI yet.

---

## Current architecture

```text
Selected Folder
   -> File Scanner
   -> Parser / OCR
   -> Privacy Redaction Layer
   -> AI Enrichment Layer
        - rules + AI classification
        - rules + AI extraction
        - AI sanitized summary
   -> Confidence + Review Flag
   -> JSON + Excel Report
   -> Optional SQLite
````

---

## Phase 1 scope

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
* rules-based classification
* basic structured extraction
* confidence scoring
* review flagging
* JSON export
* Excel export
* optional SQLite persistence
* local Streamlit browser app
* validation script
* automated tests

### Not included yet

* real AI model integration
* semantic near-duplicate detection
* advanced signature/stamp detection
* enterprise-grade access controls
* production deployment
* packaged macOS desktop app

---

## Core principles

### Privacy first

DocuScope AI is designed to avoid exposing sensitive data unnecessarily.

The MVP is built so that:

* sensitive values are masked before reporting
* outputs are sanitized
* the architecture is prepared for AI on sanitized text
* the project remains local-first by design

### Hybrid AI design

The system separates:

* deterministic software engineering tasks
* AI-powered interpretation tasks

Phase 1 includes the structure for hybrid AI, but the real AI integrations will come in later phases.

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

Phase 1 supports rules-based classification for:

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
3. extracts file metadata
4. parses text/content
5. applies OCR when needed
6. detects basic sensitive data patterns
7. masks sensitive values
8. classifies the document
9. extracts basic structured fields
10. generates a sanitized fingerprint
11. computes confidence and review status
12. exports results to JSON, Excel, and optionally SQLite

---

## Privacy model

DocuScope AI is built to generate **sanitized fingerprints**, not raw document dumps.

Examples of privacy-safe behavior:

* emails are masked
* phone numbers are masked
* IDs are masked
* summaries are sanitized
* reports are intended for structured review, not raw content exposure

Phase 1 is a privacy-aware MVP foundation. Privacy controls will continue to improve in later phases.

---

## Project structure

```text
docuscope-ai/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── models/
│   │   └── fingerprint.py
│   ├── scanner/
│   │   └── folder_scanner.py
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
│   │   └── ai_classifier.py
│   ├── extract/
│   │   ├── regex_extractors.py
│   │   └── ai_extractor.py
│   ├── summarize/
│   │   └── ai_summarizer.py
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
├── streamlit_app.py
├── requirements.txt
├── pytest.ini
└── README.md
```

---

## Installation

### 1. Create a virtual environment

```bash
python3 -m venv .venv
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

## Run locally (browser app)

DocuScope AI also includes a local Streamlit app.

```bash
streamlit run streamlit_app.py
```

This provides a simple local browser UI to:

* enter a folder path
* run a scan
* view sanitized results
* generate outputs

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

---

## Phase 1 completion criteria

Phase 1 is complete when:

* required project structure exists
* required modules exist
* imports work
* tests pass
* scanner works
* parsers work
* privacy modules work
* exports work
* validation passes

---

## Current limitations

Phase 1 is intentionally lightweight.

Current limitations include:

* AI classifier is still a placeholder
* AI extractor is still a placeholder
* AI summarizer is still a placeholder
* duplicate detection is exact-hash only
* PII detection is basic pattern-based
* language detection is heuristic
* signature/stamp detection is not fully implemented
* no production deployment yet
* no packaged macOS desktop app yet

---

## Roadmap

### Phase 2

* integrate real AI summarization
* add real AI classification fallback
* add real AI extraction fallback

### Phase 3

* improve privacy rules
* improve duplicate detection
* improve structured extraction
* improve review workflow

### Phase 4

* improve local UI
* package for macOS
* harden for production scenarios

## Author

**He-Isa**

DocuScope AI — Privacy-first hybrid AI document fingerprinting
