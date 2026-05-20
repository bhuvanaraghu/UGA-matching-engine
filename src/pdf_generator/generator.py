"""Orchestrator for match report PDF generation."""

from __future__ import annotations

import re
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from src.pdf_generator.models import MatchReport
from src.pdf_generator.renderer import PDFRenderer
from src.pdf_generator import styles as s


class PageManager:
    """Tracks pagination and coordinates page breaks."""

    def __init__(
        self,
        pdf_canvas: canvas.Canvas,
        report: MatchReport,
        total_pages: int = 1,
        draw_footers: bool = True,
    ) -> None:
        self.canvas = pdf_canvas
        self.report = report
        self.total_pages = max(1, total_pages)
        self.draw_footers = draw_footers
        self.page_num = 1
        self.y = 0.0
        self.is_first_page = True
        self.list_view_last_page = 1
        self._renderer: PDFRenderer | None = None

    def bind_renderer(self, renderer: PDFRenderer) -> None:
        self._renderer = renderer

    def new_page(self, condensed: bool = True) -> None:
        if self.draw_footers and self.total_pages > 0 and self._renderer:
            self._renderer.draw_footer(self.page_num, self.total_pages)
        self.canvas.showPage()
        self.canvas.setFillColor(s.COLOR_PAGE_BG)
        self.canvas.rect(0, 0, s.PAGE_W, s.PAGE_H, fill=1, stroke=0)
        self.page_num += 1
        self.is_first_page = False
        if condensed and self._renderer:
            self.y = self._renderer.draw_condensed_header()
        else:
            self.y = s.MARGIN_T

    def start_detail_view(self) -> None:
        """Begin detail section on a new page; record last list-view page."""
        self.list_view_last_page = self.page_num
        self.new_page(condensed=True)


def _count_pdf_pages(pdf_bytes: bytes) -> int:
    matches = len(re.findall(rb"/Type\s*/Page\b", pdf_bytes))
    return max(1, matches)


def _render_pass(
    report: MatchReport,
    target: canvas.Canvas,
    total_pages: int,
    draw_footers: bool,
) -> PageManager:
    pm = PageManager(target, report, total_pages=total_pages, draw_footers=draw_footers)
    renderer = PDFRenderer(pm, report)
    pm.bind_renderer(renderer)
    target.setFillColor(s.COLOR_PAGE_BG)
    target.rect(0, 0, s.PAGE_W, s.PAGE_H, fill=1, stroke=0)
    renderer.render()
    return pm


def generate(report: MatchReport, output_path: str) -> str:
    """
    Render the full PDF to output_path.

    Returns output_path on success.
    Raises ValueError if report.contacts is empty.
    """
    if not report.contacts:
        raise ValueError("Cannot generate PDF: report.contacts is empty")

    buffer = BytesIO()
    pass1 = canvas.Canvas(buffer, pagesize=letter)
    _render_pass(report, pass1, total_pages=1, draw_footers=False)
    pass1.save()
    total_pages = _count_pdf_pages(buffer.getvalue())

    final = canvas.Canvas(output_path, pagesize=letter)
    _render_pass(report, final, total_pages=total_pages, draw_footers=True)
    final.save()
    return output_path
