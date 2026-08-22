from pathlib import Path

from app.pipeline import run_pipeline


def _make_sample_folder(tmp_path: Path) -> Path:
    folder = tmp_path / "docs"
    folder.mkdir()
    (folder / "invoice.txt").write_text(
        "INVOICE\nInvoice Number: INV-100\nAmount Due: $42.00\nContact: a@example.com",
        encoding="utf-8",
    )
    (folder / "note.txt").write_text("Just a short unrelated note.", encoding="utf-8")
    return folder


def test_run_pipeline_returns_fingerprints_for_each_file(tmp_path) -> None:
    folder = _make_sample_folder(tmp_path)
    output = tmp_path / "out"

    fingerprints = run_pipeline(folder, output)

    assert len(fingerprints) == 2
    names = {fp.file_info.file_name for fp in fingerprints}
    assert names == {"invoice.txt", "note.txt"}


def test_run_pipeline_exports_json_and_excel(tmp_path) -> None:
    folder = _make_sample_folder(tmp_path)
    output = tmp_path / "out"

    fingerprints = run_pipeline(folder, output)

    json_files = list((output / "json").glob("*.json"))
    assert len(json_files) == len(fingerprints)
    assert (output / "document_report.xlsx").exists()


def test_run_pipeline_invokes_on_result_callback(tmp_path) -> None:
    folder = _make_sample_folder(tmp_path)
    output = tmp_path / "out"
    seen = []

    run_pipeline(folder, output, on_result=seen.append)

    assert len(seen) == 2


def test_run_pipeline_sqlite_off_by_default(tmp_path) -> None:
    folder = _make_sample_folder(tmp_path)
    output = tmp_path / "out"

    run_pipeline(folder, output)

    assert not (output / "docuscope_ai.db").exists()


def test_run_pipeline_sqlite_on_creates_db(tmp_path) -> None:
    folder = _make_sample_folder(tmp_path)
    output = tmp_path / "out"

    run_pipeline(folder, output, use_sqlite=True)

    assert (output / "docuscope_ai.db").exists()


def test_run_pipeline_continues_after_export_failure(tmp_path, monkeypatch) -> None:
    """
    The per-file try/except must cover the whole body (build + export +
    sqlite + callback), not just build_fingerprint — a failure exporting one
    file must not abort processing of the rest of the batch.
    """
    folder = _make_sample_folder(tmp_path)
    output = tmp_path / "out"

    real_export = __import__(
        "app.pipeline", fromlist=["export_fingerprint_json"]
    ).export_fingerprint_json

    def flaky_export(fp, output_dir):
        if fp.file_info.file_name == "invoice.txt":
            raise OSError("simulated disk error")
        return real_export(fp, output_dir)

    monkeypatch.setattr("app.pipeline.export_fingerprint_json", flaky_export)

    fingerprints = run_pipeline(folder, output)  # must not raise

    names = {fp.file_info.file_name for fp in fingerprints}
    assert "note.txt" in names  # processed despite invoice.txt's export failing

    json_files = list((output / "json").glob("*.json"))
    assert len(json_files) == 1  # only note.txt's export actually succeeded


def test_run_pipeline_skips_failing_file_and_continues(tmp_path, monkeypatch) -> None:
    folder = _make_sample_folder(tmp_path)
    output = tmp_path / "out"

    original_build = "app.pipeline.build_fingerprint"
    real_build_fingerprint = __import__("app.pipeline", fromlist=["build_fingerprint"]).build_fingerprint

    def flaky_build_fingerprint(file_path, seen_hashes, root_folder):
        if file_path.name == "note.txt":
            raise ValueError("simulated parse failure")
        return real_build_fingerprint(file_path, seen_hashes, root_folder)

    monkeypatch.setattr(original_build, flaky_build_fingerprint)

    fingerprints = run_pipeline(folder, output)

    assert len(fingerprints) == 1
    assert fingerprints[0].file_info.file_name == "invoice.txt"
