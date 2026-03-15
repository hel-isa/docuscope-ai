from __future__ import annotations

import argparse
from pathlib import Path

from app.scanner.folder_scanner import scan_folder, is_supported_file


def main() -> None:
    parser = argparse.ArgumentParser(description="DocuScope AI MVP")
    parser.add_argument("--input", required=True, help="Path to file or folder to process")
    args = parser.parse_args()

    input_path = Path(args.input)

    if input_path.is_file():
        if is_supported_file(input_path):
            files = [input_path]
        else:
            print(f"Unsupported file type: {input_path}")
            return
    elif input_path.is_dir():
        files = scan_folder(args.input)
    else:
        print(f"Path does not exist: {input_path}")
        return

    print(f"Found {len(files)} supported files:")
    for file_path in files:
        print(file_path)


if __name__ == "__main__":
    main()
