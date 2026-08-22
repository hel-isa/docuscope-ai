from __future__ import annotations

import json
import re
from pathlib import Path

import pydantic
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import config
from app.api.schemas import ScanRequest
from app.models.fingerprint import DocumentFingerprint
from app.pipeline import run_pipeline

STATIC_DIR = Path(__file__).parent / "static"

# document_id is always a str(uuid4()) (see app/models/fingerprint.py). This
# whitelist rejects anything else before it's used to build a file path,
# closing off path traversal via a crafted document_id (e.g. "../../etc/hosts").
_DOCUMENT_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")

app = FastAPI(
    title="DocuScope AI",
    description=(
        "Local demo API for DocuScope AI. This is a single-operator, "
        "localhost-only demo surface with no authentication — do not expose "
        "it to a network or run it as a multi-tenant service."
    ),
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def _validate_input_folder(input_folder: str) -> Path:
    """
    Resolves the submitted path and, when API_ALLOWED_ROOT is configured,
    rejects anything outside it. This is an opt-in, off-by-default
    defense-in-depth knob for a trusted local demo — not a hard sandbox.
    """
    resolved = Path(input_folder).resolve()

    if config.API_ALLOWED_ROOT:
        allowed_root = Path(config.API_ALLOWED_ROOT).resolve()
        if allowed_root != resolved and allowed_root not in resolved.parents:
            raise HTTPException(
                status_code=403,
                detail=f"input_folder must be within the allowed root: {allowed_root}",
            )

    return resolved


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/scan", response_model=list[DocumentFingerprint])
def scan(request: ScanRequest) -> list[DocumentFingerprint]:
    input_folder = _validate_input_folder(request.input_folder)

    try:
        return run_pipeline(
            input_folder, config.OUTPUT_DIR, use_sqlite=request.sqlite
        )
    except (FileNotFoundError, NotADirectoryError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        # Anything else (e.g. a SQLite/disk error from init_db, which runs
        # outside run_pipeline's own per-file error handling) must not leak
        # internals — a stack trace or file path — back to an API client.
        raise HTTPException(status_code=500, detail="Scan failed unexpectedly") from exc


@app.get("/documents", response_model=list[DocumentFingerprint])
def list_documents() -> list[DocumentFingerprint]:
    json_dir = Path(config.OUTPUT_DIR) / "json"
    if not json_dir.exists():
        return []

    fingerprints = []
    for path in sorted(json_dir.glob("*.json")):
        try:
            with path.open("r", encoding="utf-8") as f:
                fingerprints.append(DocumentFingerprint.model_validate(json.load(f)))
        except (json.JSONDecodeError, pydantic.ValidationError):
            # A stale/corrupt/pre-schema-change file must not take down the
            # whole listing — skip it and keep serving the rest.
            continue

    return fingerprints


@app.get("/documents/{document_id}", response_model=DocumentFingerprint)
def get_document(document_id: str) -> DocumentFingerprint:
    if not _DOCUMENT_ID_RE.match(document_id):
        raise HTTPException(status_code=400, detail="Invalid document_id")

    path = Path(config.OUTPUT_DIR) / "json" / f"{document_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        with path.open("r", encoding="utf-8") as f:
            return DocumentFingerprint.model_validate(json.load(f))
    except (json.JSONDecodeError, pydantic.ValidationError) as exc:
        raise HTTPException(status_code=404, detail="Document not found") from exc
