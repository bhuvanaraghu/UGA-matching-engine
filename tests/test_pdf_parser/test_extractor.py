"""Tests for PDF text extraction."""

from unittest.mock import MagicMock, patch

import pytest

from src.pdf_parser.extractor import (
    DefaultPDFExtractor,
    ExtractionError,
)


def test_raises_when_file_not_found():
    extractor = DefaultPDFExtractor()
    with pytest.raises(ExtractionError, match="not found"):
        extractor.extract(["/nonexistent/file.pdf"])


def test_raises_when_not_pdf(tmp_path):
    not_pdf = tmp_path / "notes.txt"
    not_pdf.write_text("not a pdf", encoding="utf-8")
    extractor = DefaultPDFExtractor()
    with pytest.raises(ExtractionError, match="Not a PDF"):
        extractor.extract([str(not_pdf)])


def test_raises_when_no_paths():
    extractor = DefaultPDFExtractor()
    with pytest.raises(ExtractionError, match="No PDF paths"):
        extractor.extract([])


@patch("pdfplumber.open")
def test_extract_concatenates_multiple_files(mock_open, tmp_path):
    pdf1 = tmp_path / "program_part1.pdf"
    pdf2 = tmp_path / "program_part2.pdf"
    pdf1.write_bytes(b"%PDF-1.4")
    pdf2.write_bytes(b"%PDF-1.4")

    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Sample program text."
    mock_pdf = MagicMock()
    mock_pdf.pages = [mock_page]
    mock_open.return_value.__enter__.return_value = mock_pdf

    extractor = DefaultPDFExtractor()
    result = extractor.extract([str(pdf1), str(pdf2)])

    assert "program_part1.pdf" in result
    assert "program_part2.pdf" in result
    assert "Sample program text" in result
    assert mock_open.call_count == 2


@patch("pdfplumber.open")
def test_raises_when_no_text_extracted(mock_open, tmp_path):
    pdf = tmp_path / "empty.pdf"
    pdf.write_bytes(b"%PDF-1.4")

    mock_page = MagicMock()
    mock_page.extract_text.return_value = ""
    mock_pdf = MagicMock()
    mock_pdf.pages = [mock_page]
    mock_open.return_value.__enter__.return_value = mock_pdf

    extractor = DefaultPDFExtractor()
    with pytest.raises(ExtractionError, match="No text extracted"):
        extractor.extract([str(pdf)])
