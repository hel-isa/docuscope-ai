from __future__ import annotations

import argparse

from app.scanner.folder_scanner import scan_folder


def main() -> None:
    parser = argparse.ArgumentParser(description="DocuScope AI MVP")
    parser.add_argument("--input", required=True, help="Folder to scan")
    args = parser.parse_args()

    files = scan_folder(args.input)

    print(f"Found {len(files)} supported files:")
    for file_path in files:
        print(file_path)


if __name__ == "__main__":
    main()
