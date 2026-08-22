from pathlib import Path

from fastapi.testclient import TestClient

from app.api.server import app


def _make_sample_folder(tmp_path: Path) -> Path:
    folder = tmp_path / "docs"
    folder.mkdir()
    (folder / "invoice.txt").write_text(
        "INVOICE\nInvoice Number: INV-100\nAmount Due: $42.00", encoding="utf-8"
    )
    return folder


def test_index_returns_html() -> None:
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "DocuScope AI" in response.text


def test_scan_happy_path(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("app.api.server.config.OUTPUT_DIR", tmp_path / "out")
    folder = _make_sample_folder(tmp_path)
    client = TestClient(app)

    response = client.post("/scan", json={"input_folder": str(folder)})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["file_info"]["file_name"] == "invoice.txt"


def test_scan_invalid_folder_returns_400(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("app.api.server.config.OUTPUT_DIR", tmp_path / "out")
    client = TestClient(app)

    response = client.post("/scan", json={"input_folder": str(tmp_path / "does-not-exist")})

    assert response.status_code == 400


def test_documents_round_trip(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("app.api.server.config.OUTPUT_DIR", tmp_path / "out")
    folder = _make_sample_folder(tmp_path)
    client = TestClient(app)

    scan_response = client.post("/scan", json={"input_folder": str(folder)})
    document_id = scan_response.json()[0]["document_id"]

    list_response = client.get("/documents")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    get_response = client.get(f"/documents/{document_id}")
    assert get_response.status_code == 200
    assert get_response.json()["document_id"] == document_id


def test_documents_missing_returns_404(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("app.api.server.config.OUTPUT_DIR", tmp_path / "out")
    client = TestClient(app)

    response = client.get("/documents/does-not-exist")

    assert response.status_code == 404


def test_document_id_path_traversal_rejected(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("app.api.server.config.OUTPUT_DIR", tmp_path / "out")
    client = TestClient(app)

    response = client.get("/documents/..%2F..%2F..%2Fetc%2Fpasswd")

    assert response.status_code in (400, 404)


def test_scan_rejects_path_outside_allowed_root(tmp_path, monkeypatch) -> None:
    allowed_root = tmp_path / "allowed"
    allowed_root.mkdir()
    monkeypatch.setattr("app.api.server.config.OUTPUT_DIR", tmp_path / "out")
    monkeypatch.setattr("app.api.server.config.API_ALLOWED_ROOT", str(allowed_root))
    outside_folder = _make_sample_folder(tmp_path)
    client = TestClient(app)

    response = client.post("/scan", json={"input_folder": str(outside_folder)})

    assert response.status_code == 403


def test_scan_allows_path_inside_allowed_root(tmp_path, monkeypatch) -> None:
    allowed_root = tmp_path / "allowed"
    allowed_root.mkdir()
    monkeypatch.setattr("app.api.server.config.OUTPUT_DIR", tmp_path / "out")
    monkeypatch.setattr("app.api.server.config.API_ALLOWED_ROOT", str(allowed_root))
    (allowed_root / "invoice.txt").write_text("INVOICE\nAmount Due: $1.00", encoding="utf-8")
    client = TestClient(app)

    response = client.post("/scan", json={"input_folder": str(allowed_root)})

    assert response.status_code == 200


def test_scan_unexpected_error_returns_clean_500_without_leaking_details(
    tmp_path, monkeypatch
) -> None:
    """
    An unexpected failure (e.g. a SQLite/disk error from init_db, which runs
    outside run_pipeline's own per-file error handling) must surface as a
    generic 500, never a raw stack trace or internal detail to the client.
    """
    monkeypatch.setattr("app.api.server.config.OUTPUT_DIR", tmp_path / "out")
    folder = _make_sample_folder(tmp_path)

    def boom(*args, **kwargs):
        raise RuntimeError("simulated internal failure with a sensitive path /etc/secret")

    monkeypatch.setattr("app.api.server.run_pipeline", boom)
    client = TestClient(app, raise_server_exceptions=False)

    response = client.post("/scan", json={"input_folder": str(folder)})

    assert response.status_code == 500
    assert "sensitive path" not in response.text
    assert response.json()["detail"] == "Scan failed unexpectedly"
