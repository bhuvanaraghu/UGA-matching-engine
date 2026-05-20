"""Tests for PDF generation (file output, no visual assertions)."""

import re

import pytest

from src.pdf_generator.generator import _render_pass, generate


def test_generate_creates_valid_pdf(sample_match_report, tmp_path):
    output_path = tmp_path / "test_matches.pdf"
    result = generate(sample_match_report, str(output_path))

    assert result == str(output_path)
    assert output_path.exists()
    assert output_path.stat().st_size > 0
    assert output_path.read_bytes().startswith(b"%PDF")


def test_generate_raises_on_empty_contacts(sample_match_report, tmp_path):
    report = sample_match_report.model_copy(update={"contacts": []})
    with pytest.raises(ValueError, match="empty"):
        generate(report, str(tmp_path / "empty.pdf"))


def test_weak_contact_excluded_from_detail_contact_set(sample_match_report):
    """Detail cards only render strong + medium — weak is not in that set."""
    weak_name = "Meadow Creek Farms"
    detail_contacts = sample_match_report.strong + sample_match_report.medium
    assert any(c.company_name == weak_name for c in sample_match_report.weak)
    assert weak_name not in [c.company_name for c in detail_contacts]


def test_detail_view_starts_on_page_after_list(sample_match_report):
    """Detail section begins on a new page after list view ends."""
    from io import BytesIO

    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    pm = _render_pass(sample_match_report, c, total_pages=3, draw_footers=False)
    c.save()

    assert pm.list_view_last_page >= 1
    assert pm.page_num > pm.list_view_last_page

    page_count = len(re.findall(rb"/Type\s*/Page\b", buffer.getvalue()))
    assert page_count >= 2


def test_gap_questions_on_medium_contacts(sample_match_report):
    medium_with_gaps = [c for c in sample_match_report.medium if c.gap_questions]
    assert len(medium_with_gaps) == 2
