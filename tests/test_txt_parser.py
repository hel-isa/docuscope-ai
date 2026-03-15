from pathlib import Path

from app.parsers.txt_parser import parse_txt


def test_parse_txt(tmp_path: Path) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("Hello world", encoding="utf-8")

    result = parse_txt(sample)

    assert result["text"] == "Hello world"
    assert result["page_count"] == 1
    assert result["ocr_needed"] is False
    assert result["ocr_used"] is False
