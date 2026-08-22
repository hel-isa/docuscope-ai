from __future__ import annotations

import zipfile
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL import Image as ImageModule

_DEFAULT_MAX_ZIP_RATIO = 100.0
_DEFAULT_MAX_ZIP_ENTRIES = 10_000


class ResourceLimitExceeded(Exception):
    """Base class for all resource-exhaustion guard failures. Every parser
    that raises one of these is signalling a file that must be rejected, not
    silently skipped or truncated. Inherits from Exception so it's caught for
    free by the pipeline's existing generic per-file error handling."""


class FileTooLargeError(ResourceLimitExceeded):
    pass


class ZipBombSuspectedError(ResourceLimitExceeded):
    pass


class PdfTooManyPagesError(ResourceLimitExceeded):
    pass


class ImageTooLargeError(ResourceLimitExceeded):
    pass


def check_file_size(path: Path, max_bytes: int) -> None:
    """Universal gate: rejects any file above the configured size before it
    is handed to a parser at all."""
    size = path.stat().st_size
    if size > max_bytes:
        raise FileTooLargeError(
            f"File exceeds maximum allowed size: {size} bytes > {max_bytes} bytes ({path.name})"
        )


def check_zip_container(
    path: Path,
    max_uncompressed_bytes: int,
    max_ratio: float = _DEFAULT_MAX_ZIP_RATIO,
    max_entries: int = _DEFAULT_MAX_ZIP_ENTRIES,
) -> None:
    """DOCX and XLSX files are zip containers. This reads only the central
    directory (no decompression) and rejects files that would expand far
    beyond their on-disk size, contain an excessive number of entries, or
    have any single entry with a suspiciously extreme compression ratio —
    the classic "zip bomb" pattern.

    Known residual risk: this trusts the size/ratio metadata declared in the
    central directory rather than cross-checking it against the actual
    decompressed byte stream. A file that lies about its own metadata could
    slip past this fast, non-decompressing pre-check. Closing that gap fully
    would require a streaming, size-bounded read during actual decompression
    (in python-docx/openpyxl) — out of scope here; this guard is a first,
    cheap layer, not the only one."""
    with zipfile.ZipFile(path) as zf:
        infos = zf.infolist()

        if len(infos) > max_entries:
            raise ZipBombSuspectedError(
                f"Zip container has too many entries: {len(infos)} > {max_entries} ({path.name})"
            )

        total_uncompressed = sum(info.file_size for info in infos)
        if total_uncompressed > max_uncompressed_bytes:
            raise ZipBombSuspectedError(
                f"Zip container would expand beyond the allowed limit: "
                f"{total_uncompressed} bytes > {max_uncompressed_bytes} bytes ({path.name})"
            )

        for info in infos:
            if info.compress_size > 0:
                ratio = info.file_size / info.compress_size
                if ratio > max_ratio:
                    raise ZipBombSuspectedError(
                        f"Zip entry '{info.filename}' has a suspicious compression ratio: "
                        f"{ratio:.1f}x > {max_ratio}x ({path.name})"
                    )
            elif info.file_size > 0:
                raise ZipBombSuspectedError(
                    f"Zip entry '{info.filename}' claims uncompressed content from zero "
                    f"compressed bytes ({path.name})"
                )


def check_pdf_page_count(page_count: int, max_pages: int) -> None:
    if page_count > max_pages:
        raise PdfTooManyPagesError(f"PDF has too many pages: {page_count} > {max_pages}")


def configure_pillow_limits(max_pixels: int) -> None:
    """Sets Pillow's global decompression-bomb threshold. Safe to call
    repeatedly/from multiple modules; the last call wins, which is fine since
    every caller passes the same configured limit.

    Note: Pillow only *raises* DecompressionBombError above 2x this value —
    between 1x and 2x it only issues a non-fatal warning. open_image_safely()
    below is the authoritative check; this call is defense-in-depth for any
    other Pillow operation that consults the global threshold directly."""
    from PIL import Image

    Image.MAX_IMAGE_PIXELS = max_pixels


def open_image_safely(path: Path, max_pixels: int) -> "ImageModule.Image":
    """Opens an image and enforces max_pixels as a hard limit, exactly at the
    configured threshold — not Pillow's own 2x-buffered exception behavior.
    Centralizing this (instead of each caller wrapping Image.open() itself)
    keeps the pixel-limit enforcement exact and in one place."""
    from PIL import Image

    try:
        img = Image.open(path)
    except Image.DecompressionBombError as e:
        raise ImageTooLargeError(f"Image exceeds the allowed pixel limit: {path}: {e}") from e

    width, height = img.size
    pixels = max(1, width) * max(1, height)
    if pixels > max_pixels:
        raise ImageTooLargeError(
            f"Image exceeds the allowed pixel limit: {pixels} pixels > {max_pixels} pixels ({path.name})"
        )

    return img
