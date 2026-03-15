from pathlib import Path

from app.scanner.folder_scanner import is_supported_file, scan_folder


def test_is_supported_file(tmp_path: Path) -> None:
    pdf_file = tmp_path / "sample.pdf"
    pdf_file.write_text("dummy")

    txt_file = tmp_path / "notes.txt"
    txt_file.write_text("hello")

    zip_file = tmp_path / "archive.zip"
    zip_file.write_text("nope")

    assert is_supported_file(pdf_file) is True
    assert is_supported_file(txt_file) is True
    assert is_supported_file(zip_file) is False


def test_scan_folder_recursive(tmp_path: Path) -> None:
    sub = tmp_path / "subfolder"
    sub.mkdir()

    file1 = tmp_path / "a.pdf"
    file1.write_text("pdf")

    file2 = sub / "b.txt"
    file2.write_text("text")

    file3 = sub / "c.zip"
    file3.write_text("zip")

    results = scan_folder(tmp_path)

    assert len(results) == 2
    assert file1 in results
    assert file2 in results
    assert file3 not in results