from __future__ import annotations

from pathlib import Path
from typing import Iterable


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".xlsx",
    ".txt",
    ".jpg",
    ".jpeg",
    ".png",
}


def is_supported_file(file_path: Path) -> bool:
    """
    Return True if the file extension is supported by the MVP.
    """
    return file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS


def scan_folder(root_folder: str | Path) -> list[Path]:
    """
    Recursively scan a folder and return all supported files.
    """
    root = Path(root_folder)

    if not root.exists():
        raise FileNotFoundError(f"Folder does not exist: {root}")

    if not root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {root}")

    files: list[Path] = []

    for path in root.rglob("*"):
        if is_supported_file(path):
            files.append(path)

    return sorted(files)


def iter_supported_files(root_folder: str | Path) -> Iterable[Path]:
    """
    Generator version of scan_folder for large folders.
    Useful later if you want streaming-style processing.
    """
    root = Path(root_folder)

    if not root.exists():
        raise FileNotFoundError(f"Folder does not exist: {root}")

    if not root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {root}")

    for path in root.rglob("*"):
        if is_supported_file(path):
            yield path