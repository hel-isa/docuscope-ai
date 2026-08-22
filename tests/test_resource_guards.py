import zipfile

import pytest
from PIL import Image
from pypdf import PdfWriter

from app.security.resource_guards import (
    FileTooLargeError,
    ImageTooLargeError,
    PdfTooManyPagesError,
    ZipBombSuspectedError,
    check_file_size,
    check_pdf_page_count,
    check_zip_container,
    configure_pillow_limits,
    open_image_safely,
)


def test_check_file_size_passes_under_limit(tmp_path) -> None:
    f = tmp_path / "small.txt"
    f.write_text("hello")

    check_file_size(f, max_bytes=1024)  # should not raise


def test_check_file_size_rejects_over_limit(tmp_path) -> None:
    f = tmp_path / "big.txt"
    f.write_bytes(b"x" * 2048)

    with pytest.raises(FileTooLargeError):
        check_file_size(f, max_bytes=1024)


def test_check_pdf_page_count_passes_under_limit() -> None:
    check_pdf_page_count(page_count=5, max_pages=10)  # should not raise


def test_check_pdf_page_count_rejects_over_limit() -> None:
    with pytest.raises(PdfTooManyPagesError):
        check_pdf_page_count(page_count=600, max_pages=500)


def test_check_pdf_page_count_rejects_many_real_pages(tmp_path) -> None:
    writer = PdfWriter()
    for _ in range(20):
        writer.add_blank_page(width=72, height=72)

    out = tmp_path / "many_pages.pdf"
    with out.open("wb") as f:
        writer.write(f)

    from pypdf import PdfReader

    reader = PdfReader(str(out))
    with pytest.raises(PdfTooManyPagesError):
        check_pdf_page_count(len(reader.pages), max_pages=10)


def test_check_zip_container_passes_normal_archive(tmp_path) -> None:
    f = tmp_path / "normal.zip"
    with zipfile.ZipFile(f, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("word/document.xml", "<xml>hello world</xml>" * 10)

    check_zip_container(f, max_uncompressed_bytes=10_000_000)  # should not raise


def test_check_zip_container_rejects_excessive_total_size(tmp_path) -> None:
    f = tmp_path / "big.zip"
    with zipfile.ZipFile(f, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("data.txt", "a" * 1000)

    with pytest.raises(ZipBombSuspectedError):
        check_zip_container(f, max_uncompressed_bytes=100)


def test_check_zip_container_rejects_suspicious_compression_ratio(tmp_path) -> None:
    """
    A classic zip-bomb pattern: a small amount of highly-repetitive data that
    compresses to a tiny footprint but expands enormously.
    """
    f = tmp_path / "bomb.zip"
    huge_repetitive_content = "0" * 50_000_000  # compresses to a few KB
    with zipfile.ZipFile(f, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("data.txt", huge_repetitive_content)

    # Total size is under the byte cap, but the ratio check must still catch it.
    with pytest.raises(ZipBombSuspectedError):
        check_zip_container(f, max_uncompressed_bytes=1_000_000_000, max_ratio=100.0)


def test_check_zip_container_rejects_too_many_entries(tmp_path) -> None:
    f = tmp_path / "many_entries.zip"
    with zipfile.ZipFile(f, "w", zipfile.ZIP_DEFLATED) as zf:
        for i in range(50):
            zf.writestr(f"entry_{i}.txt", "x")

    with pytest.raises(ZipBombSuspectedError):
        check_zip_container(f, max_uncompressed_bytes=10_000_000, max_entries=10)


def test_configure_pillow_limits_rejects_oversized_image(tmp_path, monkeypatch) -> None:
    configure_pillow_limits(max_pixels=100)  # tiny limit for this test

    f = tmp_path / "normal.png"
    Image.new("RGB", (50, 50), color=(255, 0, 0)).save(f)

    with pytest.raises(Image.DecompressionBombError):
        Image.open(f)

    configure_pillow_limits(max_pixels=50_000_000)  # restore a sane default


def test_open_image_safely_rejects_image_in_1x_to_2x_warning_only_range(tmp_path) -> None:
    """
    Pillow's own Image.open() only *raises* above 2x MAX_IMAGE_PIXELS; between
    1x and 2x it only issues a non-fatal DecompressionBombWarning and returns
    normally. open_image_safely() must enforce the limit itself rather than
    relying solely on Pillow's exception behavior.
    """
    max_pixels = 100
    # 15x15 = 225 pixels: > 1x (100) but < 2x (200)... use a size that's
    # clearly inside the 1x-2x band relative to the configured limit.
    width, height = 13, 12  # 156 pixels: 1.56x the limit, inside the warn-only band
    f = tmp_path / "mid_range.png"
    Image.new("RGB", (width, height), color=(0, 200, 0)).save(f)

    configure_pillow_limits(max_pixels=max_pixels)
    try:
        # Confirm Pillow itself would only warn, not raise, for this size.
        import warnings

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            Image.open(f)
            assert any(issubclass(w.category, Image.DecompressionBombWarning) for w in caught)

        # The shared helper must still reject it.
        with pytest.raises(ImageTooLargeError):
            open_image_safely(f, max_pixels)
    finally:
        configure_pillow_limits(max_pixels=50_000_000)  # restore a sane default
