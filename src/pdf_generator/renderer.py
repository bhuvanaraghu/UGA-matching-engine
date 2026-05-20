"""ReportLab canvas rendering for branded match report PDFs."""

from __future__ import annotations

import math
from datetime import datetime
from typing import List, Optional, Tuple

from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas

from src.pdf_generator.models import MatchReport, MatchStrength, MatchedContact
from src.pdf_generator import styles as s


def format_run_date(iso_date: str) -> str:
    """Convert ISO date to 'Month DD, YYYY'."""
    try:
        dt = datetime.strptime(iso_date, "%Y-%m-%d")
        return dt.strftime("%B %d, %Y")
    except ValueError:
        return iso_date


def badge_label(strength: MatchStrength) -> str:
    if strength == MatchStrength.STRONG:
        return "Strong"
    if strength == MatchStrength.MEDIUM:
        return "Medium"
    return "Verify"


def badge_style(strength: MatchStrength) -> Tuple[object, object, bool]:
    """Return fill color, text color, draw_border."""
    if strength == MatchStrength.STRONG:
        return s.COLOR_STRONG_FILL, s.COLOR_STRONG_TEXT, False
    if strength == MatchStrength.MEDIUM:
        return s.COLOR_MEDIUM_FILL, s.COLOR_MEDIUM_TEXT, False
    return s.COLOR_WEAK_FILL, s.COLOR_WEAK_TEXT, True


class PDFRenderer:
    """Renders a MatchReport using a PageManager for pagination."""

    def __init__(self, page_manager: "PageManager", report: MatchReport) -> None:
        self.pm = page_manager
        self.report = report

    @property
    def c(self) -> canvas.Canvas:
        return self.pm.canvas

    def y_rl(self, y_top: float) -> float:
        return s.PAGE_H - y_top

    def render(self) -> None:
        self.pm.y = self.draw_header()
        self.pm.y = self.draw_summary_bar(self.pm.y)
        self.draw_list_view(self.pm.y)
        self.pm.start_detail_view()
        self.draw_detail_view()
        if self.pm.draw_footers and self.pm.total_pages > 0:
            self.draw_footer(self.pm.page_num, self.pm.total_pages)

    def draw_header(self) -> float:
        c = self.c
        report = self.report
        y = s.MARGIN_T

        logo = 30
        logo_x = s.MARGIN_L
        c.setFillColor(s.COLOR_ACCENT)
        c.roundRect(logo_x, self.y_rl(y + logo), logo, logo, 6, fill=1, stroke=0)
        c.setFillColor(s.COLOR_WHITE)
        c.setFont(s.FONT_BOLD, 13)
        c.drawCentredString(logo_x + logo / 2, self.y_rl(y + logo / 2 + 4), "P")

        text_x = logo_x + logo + 10
        c.setFillColor(s.COLOR_TEXT_PRIMARY)
        c.setFont(s.FONT_BOLD, s.SIZE_BRAND_NAME)
        c.drawString(text_x, self.y_rl(y + 14), "Prism Digital Labs")
        c.setFillColor(s.COLOR_TEXT_MUTED)
        c.setFont(s.FONT_REGULAR, s.SIZE_BRAND_SUB)
        c.drawString(text_x, self.y_rl(y + 28), "Prepared for United Grants of America")

        right_x = s.MARGIN_L + s.CONTENT_W
        page_line = (
            f"{format_run_date(report.run_date)} · "
            f"Page {self.pm.page_num} of {self.pm.total_pages}"
        )
        c.setFillColor(s.COLOR_ACCENT)
        c.setFont(s.FONT_BOLD, s.SIZE_EYEBROW)
        c.drawRightString(right_x, self.y_rl(y + 10), "ELIGIBLE CLIENTS — PROGRAM MATCH")
        c.setFillColor(s.COLOR_TEXT_PRIMARY)
        c.setFont(s.FONT_BOLD, s.SIZE_PROG_NAME)
        c.drawRightString(right_x, self.y_rl(y + 28), report.program_name)
        c.setFillColor(s.COLOR_TEXT_MUTED)
        c.setFont(s.FONT_REGULAR, s.SIZE_RUN_DATE)
        c.drawRightString(right_x, self.y_rl(y + 42), page_line)

        rule_y = y + 52
        c.setStrokeColor(s.COLOR_ACCENT)
        c.setLineWidth(2)
        c.line(s.MARGIN_L, self.y_rl(rule_y), right_x, self.y_rl(rule_y))
        return rule_y + 12 + s.GAP_AFTER_HEADER_RULE

    def draw_condensed_header(self) -> float:
        c = self.c
        y = s.MARGIN_T
        left = f"Prism Digital Labs · {self.report.program_name} · Eligible client matches"
        right = f"Page {self.pm.page_num} of {self.pm.total_pages}"

        c.setFillColor(s.COLOR_TEXT_MUTED)
        c.setFont(s.FONT_REGULAR, s.SIZE_CONDENSED_HDR)
        prefix = "Prism Digital Labs"
        c.setFont(s.FONT_BOLD, s.SIZE_CONDENSED_HDR)
        c.drawString(s.MARGIN_L, self.y_rl(y + 12), prefix)
        rest_x = s.MARGIN_L + c.stringWidth(prefix, s.FONT_BOLD, s.SIZE_CONDENSED_HDR)
        c.setFont(s.FONT_REGULAR, s.SIZE_CONDENSED_HDR)
        c.drawString(rest_x, self.y_rl(y + 12), left[len(prefix) :])
        c.drawRightString(s.MARGIN_L + s.CONTENT_W, self.y_rl(y + 12), right)

        rule_y = y + 22
        c.setStrokeColor(s.COLOR_ACCENT)
        c.setLineWidth(1.5)
        c.line(s.MARGIN_L, self.y_rl(rule_y), s.MARGIN_L + s.CONTENT_W, self.y_rl(rule_y))
        return rule_y + 14

    def draw_summary_bar(self, y: float) -> float:
        c = self.c
        card_w = (s.CONTENT_W - 3 * s.STAT_GAP) / 4
        stats = [
            ("Total matched", str(len(self.report.contacts))),
            ("Strong", str(len(self.report.strong))),
            ("Medium", str(len(self.report.medium))),
            ("Weak", str(len(self.report.weak))),
        ]
        card_top = y
        for i, (label, value) in enumerate(stats):
            x = s.MARGIN_L + i * (card_w + s.STAT_GAP)
            c.setFillColor(s.COLOR_SURFACE)
            c.setStrokeColor(s.COLOR_BORDER)
            c.setLineWidth(0.5)
            c.roundRect(
                x,
                self.y_rl(card_top + s.STAT_CARD_H),
                card_w,
                s.STAT_CARD_H,
                s.CARD_RADIUS,
                fill=1,
                stroke=1,
            )
            c.setFillColor(s.COLOR_TEXT_MUTED)
            c.setFont(s.FONT_REGULAR, s.SIZE_STAT_LABEL)
            c.drawString(x + 10, self.y_rl(card_top + 14), label)
            c.setFillColor(s.COLOR_TEXT_PRIMARY)
            c.setFont(s.FONT_BOLD, s.SIZE_STAT_VAL)
            c.drawString(x + 10, self.y_rl(card_top + 32), value)
        return card_top + s.STAT_CARD_H + s.GAP_AFTER_SUMMARY

    def draw_section_label(self, label: str, y: float) -> float:
        c = self.c
        text = label.upper()
        c.setFillColor(s.COLOR_TEXT_MUTED)
        c.setFont(s.FONT_BOLD, s.SIZE_SEC_LABEL)
        c.drawString(s.MARGIN_L, self.y_rl(y + 10), text)
        tw = c.stringWidth(text, s.FONT_BOLD, s.SIZE_SEC_LABEL)
        c.setStrokeColor(s.COLOR_BORDER)
        c.setLineWidth(0.5)
        c.line(
            s.MARGIN_L + tw + 8,
            self.y_rl(y + 6),
            s.MARGIN_L + s.CONTENT_W,
            self.y_rl(y + 6),
        )
        return y + s.GAP_AFTER_SECTION_LABEL

    def draw_footer(self, page_num: int, total_pages: int) -> None:
        c = self.c
        y_rule = s.MARGIN_B + 18
        c.setStrokeColor(s.COLOR_BORDER)
        c.setLineWidth(0.5)
        c.line(s.MARGIN_L, y_rule + 8, s.MARGIN_L + s.CONTENT_W, y_rule + 8)
        c.setFillColor(s.COLOR_TEXT_MUTED)
        c.setFont(s.FONT_REGULAR, s.SIZE_FOOTER)
        c.drawString(
            s.MARGIN_L,
            y_rule - 2,
            "Prism Digital Labs · Confidential · For internal AE use only",
        )
        right = f"{self.report.program_name} Matching Engine · Page {page_num} of {total_pages}"
        c.drawRightString(s.MARGIN_L + s.CONTENT_W, y_rule - 2, right)

    def draw_badge(
        self,
        strength: MatchStrength,
        x_right: float,
        y_top: float,
        width: float = s.BADGE_COL_W,
    ) -> None:
        c = self.c
        label = badge_label(strength)
        fill, text_color, border = badge_style(strength)
        c.setFont(s.FONT_BOLD, s.SIZE_BADGE)
        tw = c.stringWidth(label, s.FONT_BOLD, s.SIZE_BADGE)
        pill_w = min(width, tw + 16)
        pill_h = 18
        x = x_right - pill_w
        y_bottom = self.y_rl(y_top + pill_h)
        c.setFillColor(fill)
        if border:
            c.setStrokeColor(s.COLOR_BORDER)
            c.setLineWidth(0.5)
            c.roundRect(x, y_bottom, pill_w, pill_h, s.PILL_RADIUS, fill=1, stroke=1)
        else:
            c.roundRect(x, y_bottom, pill_w, pill_h, s.PILL_RADIUS, fill=1, stroke=0)
        c.setFillColor(text_color)
        c.drawCentredString(x + pill_w / 2, y_bottom + 5, label)

    def _list_columns(self) -> Tuple[float, float, float, float, float]:
        rest = s.CONTENT_W - s.RANK_COL_W - s.BADGE_COL_W
        w_co = rest * 0.38
        w_ph = rest * 0.28
        w_ae = rest - w_co - w_ph
        return s.RANK_COL_W, w_co, w_ph, w_ae, s.BADGE_COL_W

    def _min_content_y(self) -> float:
        return s.MARGIN_T + s.FOOTER_HEIGHT + 8

    def _needs_break(self, y: float, height: float) -> bool:
        return y + height > s.PAGE_H - s.MARGIN_B - s.FOOTER_HEIGHT

    def draw_list_view(self, y: float) -> None:
        self.pm.y = y
        sections = [
            ("Strong matches", self.report.strong),
            ("Medium matches", self.report.medium),
            ("Weak matches", self.report.weak),
        ]
        for section_name, contacts in sections:
            if not contacts:
                continue
            needed = s.SECTION_GAP + s.LIST_HEADER_H + s.ROW_H * 2
            if self._needs_break(self.pm.y, needed):
                self.pm.new_page(condensed=True)
            self.pm.y += s.SECTION_GAP
            self.pm.y = self.draw_section_label(section_name, self.pm.y)
            self.pm.y = self._draw_list_header(self.pm.y)
            for idx, contact in enumerate(contacts):
                if self._needs_break(self.pm.y, s.ROW_H):
                    self.pm.new_page(condensed=True)
                    self.pm.y = self._draw_list_header(self.pm.y)
                self.pm.y = self._draw_list_row(self.pm.y, contact, idx % 2 == 1)

    def _draw_list_header(self, y: float) -> float:
        c = self.c
        c.setFillColor(s.COLOR_SURFACE)
        c.rect(
            s.MARGIN_L,
            self.y_rl(y + s.LIST_HEADER_H),
            s.CONTENT_W,
            s.LIST_HEADER_H,
            fill=1,
            stroke=0,
        )
        c.setStrokeColor(s.COLOR_BORDER)
        c.setLineWidth(0.5)
        c.line(
            s.MARGIN_L,
            self.y_rl(y + s.LIST_HEADER_H),
            s.MARGIN_L + s.CONTENT_W,
            self.y_rl(y + s.LIST_HEADER_H),
        )
        w_rank, w_co, w_ph, w_ae, w_badge = self._list_columns()
        x = s.MARGIN_L
        headers = ["#", "COMPANY / CONTACT", "PHONE / EMAIL", "ACCOUNT EXEC", "MATCH"]
        widths = [w_rank, w_co, w_ph, w_ae, w_badge]
        c.setFillColor(s.COLOR_TEXT_MUTED)
        c.setFont(s.FONT_BOLD, s.SIZE_TABLE_HEADER)
        baseline = self.y_rl(y + 14)
        for header, width in zip(headers, widths):
            if header == "MATCH":
                c.drawRightString(x + width - 4, baseline, header)
            else:
                c.drawString(x + 4, baseline, header)
            x += width
        return y + s.LIST_HEADER_H

    def _draw_list_row(self, y: float, contact: MatchedContact, alt: bool) -> float:
        c = self.c
        if alt:
            c.setFillColor(s.COLOR_SURFACE)
            c.rect(
                s.MARGIN_L,
                self.y_rl(y + s.ROW_H),
                s.CONTENT_W,
                s.ROW_H,
                fill=1,
                stroke=0,
            )
        c.setStrokeColor(s.COLOR_BORDER)
        c.setLineWidth(0.5)
        c.line(
            s.MARGIN_L,
            self.y_rl(y + s.ROW_H),
            s.MARGIN_L + s.CONTENT_W,
            self.y_rl(y + s.ROW_H),
        )
        w_rank, w_co, w_ph, w_ae, w_badge = self._list_columns()
        x = s.MARGIN_L
        base = self.y_rl(y + 16)

        c.setFillColor(s.COLOR_TEXT_MUTED)
        c.setFont(s.FONT_REGULAR, s.SIZE_TABLE_BODY)
        c.drawString(x + 4, base, str(contact.rank))
        x += w_rank

        c.setFillColor(s.COLOR_TEXT_PRIMARY)
        c.setFont(s.FONT_BOLD, s.SIZE_TABLE_BODY)
        c.drawString(x + 4, base, self._truncate(contact.company_name, w_co - 8, s.FONT_BOLD, s.SIZE_TABLE_BODY))
        c.setFillColor(s.COLOR_TEXT_MUTED)
        c.setFont(s.FONT_REGULAR, s.SIZE_TABLE_BODY - 1)
        c.drawString(
            x + 4,
            self.y_rl(y + 22),
            self._truncate(contact.point_of_contact, w_co - 8, s.FONT_REGULAR, s.SIZE_TABLE_BODY - 1),
        )
        x += w_co

        c.setFillColor(s.COLOR_TEXT_PRIMARY)
        c.setFont(s.FONT_REGULAR, s.SIZE_TABLE_BODY)
        c.drawString(x + 4, base, self._truncate(contact.phone or "—", w_ph - 8, s.FONT_REGULAR, s.SIZE_TABLE_BODY))
        c.setFillColor(s.COLOR_TEXT_MUTED)
        c.setFont(s.FONT_REGULAR, s.SIZE_TABLE_BODY - 1)
        c.drawString(
            x + 4,
            self.y_rl(y + 22),
            self._truncate(contact.email or "—", w_ph - 8, s.FONT_REGULAR, s.SIZE_TABLE_BODY - 1),
        )
        x += w_ph

        c.setFillColor(s.COLOR_TEXT_PRIMARY)
        c.setFont(s.FONT_REGULAR, s.SIZE_TABLE_BODY)
        ae = contact.account_executive or "—"
        c.drawString(x + 4, base, self._truncate(ae, w_ae - 8, s.FONT_REGULAR, s.SIZE_TABLE_BODY))
        x += w_ae

        self.draw_badge(contact.match_strength, s.MARGIN_L + s.CONTENT_W, y + 4)
        return y + s.ROW_H

    def draw_detail_view(self) -> None:
        """Strong and medium detail cards only — weak contacts excluded."""
        self.pm.y += s.SECTION_GAP
        self.pm.y = self.draw_section_label("Detail view — strong & medium matches", self.pm.y)

        for section_name, contacts in (
            ("Strong matches", self.report.strong),
            ("Medium matches", self.report.medium),
        ):
            if not contacts:
                continue
            if self._needs_break(self.pm.y, 80):
                self.pm.new_page(condensed=True)
            self.pm.y = self.draw_section_label(section_name, self.pm.y)
            for contact in contacts:
                card_h = self.estimate_card_height(contact)
                if self._needs_break(self.pm.y, card_h):
                    self.pm.new_page(condensed=True)
                self.pm.y = self.draw_card(contact, self.pm.y)
                self.pm.y += s.CARD_GAP

    def estimate_card_height(self, contact: MatchedContact) -> float:
        inner_w = s.CONTENT_W - 2 * s.CARD_PAD
        base = 72 + 2 * s.CARD_PAD + s.SAFETY_MARGIN
        lines = simpleSplit(
            contact.match_summary,
            s.FONT_REGULAR,
            s.SIZE_MATCH_BOX,
            inner_w,
        )
        reason_h = len(lines) * s.SIZE_MATCH_BOX * s.LINE_HEIGHT_BODY + 16
        pill_rows = max(1, math.ceil(len(contact.criteria_met) / 4))
        pills_h = pill_rows * (s.SIZE_PILL + s.PILL_PAD_V * 2 + 4)
        gap_h = 0.0
        if contact.gap_questions:
            gap_h = 30
            for gq in contact.gap_questions:
                q_lines = simpleSplit(gq.question, s.FONT_BOLD, s.SIZE_GAP_Q, inner_w)
                n_lines = simpleSplit(gq.note, s.FONT_REGULAR, s.SIZE_GAP_NOTE, inner_w)
                gap_h += (
                    len(q_lines) * s.SIZE_GAP_Q * s.LINE_HEIGHT_BODY
                    + len(n_lines) * s.SIZE_GAP_NOTE * s.LINE_HEIGHT_BODY
                    + s.GAP_ITEM_PAD * 2
                    + 12
                )
        return base + reason_h + pills_h + gap_h

    def draw_card(self, contact: MatchedContact, y: float) -> float:
        c = self.c
        card_h = self.estimate_card_height(contact)
        x = s.MARGIN_L
        y_bottom_rl = self.y_rl(y + card_h)

        c.setFillColor(s.COLOR_WHITE)
        c.setStrokeColor(s.COLOR_BORDER)
        c.setLineWidth(0.5)
        c.roundRect(x, y_bottom_rl, s.CONTENT_W, card_h, s.CARD_RADIUS, fill=1, stroke=1)

        inner_x = x + s.CARD_PAD
        inner_w = s.CONTENT_W - 2 * s.CARD_PAD
        cur = y + s.CARD_PAD

        c.setFillColor(s.COLOR_TEXT_MUTED)
        c.setFont(s.FONT_REGULAR, s.SIZE_CARD_RANK)
        c.drawString(inner_x, self.y_rl(cur + 12), f"#{contact.rank}")
        c.setFillColor(s.COLOR_TEXT_PRIMARY)
        c.setFont(s.FONT_BOLD, s.SIZE_CARD_CO)
        c.drawString(inner_x + 28, self.y_rl(cur + 12), self._truncate(
            contact.company_name, inner_w - 100, s.FONT_BOLD, s.SIZE_CARD_CO
        ))
        c.setFillColor(s.COLOR_TEXT_MUTED)
        c.setFont(s.FONT_REGULAR, s.SIZE_CARD_POC)
        c.drawString(inner_x + 28, self.y_rl(cur + 26), contact.point_of_contact)
        self.draw_badge(contact.match_strength, x + s.CONTENT_W - s.CARD_PAD, cur)
        cur += 36

        cur = self._draw_contact_line(inner_x, cur, inner_w, contact)
        cur += 8

        cur = self._draw_match_reason_box(inner_x, cur, inner_w, contact.match_summary)
        cur += 8

        cur = self._draw_criteria_pills(inner_x, cur, inner_w, contact.criteria_met)
        cur += 8

        if contact.account_executive:
            c.setFillColor(s.COLOR_TEXT_MUTED)
            c.setFont(s.FONT_REGULAR, s.SIZE_AE_LINE)
            c.drawString(inner_x, self.y_rl(cur + 10), "AE: ")
            ae_x = inner_x + c.stringWidth("AE: ", s.FONT_REGULAR, s.SIZE_AE_LINE)
            c.setFillColor(s.COLOR_TEXT_PRIMARY)
            c.setFont(s.FONT_BOLD, s.SIZE_AE_LINE)
            c.drawString(ae_x, self.y_rl(cur + 10), contact.account_executive)
            cur += 18

        if contact.gap_questions:
            cur = self._draw_gap_section(inner_x, cur, inner_w, contact.gap_questions)

        return y + card_h

    def _draw_contact_line(
        self,
        x: float,
        y: float,
        width: float,
        contact: MatchedContact,
    ) -> float:
        c = self.c
        parts: List[Tuple[str, bool]] = []
        if contact.phone:
            parts.append((contact.phone, True))
        if contact.email:
            parts.append((contact.email, False))
        if contact.location:
            parts.append((contact.location, True))
        if not parts:
            return y
        cx = x
        baseline = self.y_rl(y + 12)
        for i, (text, primary) in enumerate(parts):
            if i > 0:
                c.setFillColor(s.COLOR_TEXT_MUTED)
                c.setFont(s.FONT_REGULAR, s.SIZE_CARD_CONTACT)
                sep = " · "
                c.drawString(cx, baseline, sep)
                cx += c.stringWidth(sep, s.FONT_REGULAR, s.SIZE_CARD_CONTACT)
            c.setFillColor(s.COLOR_TEXT_PRIMARY if primary else s.COLOR_TEXT_MUTED)
            c.setFont(s.FONT_REGULAR, s.SIZE_CARD_CONTACT)
            c.drawString(cx, baseline, text)
            cx += c.stringWidth(text, s.FONT_REGULAR, s.SIZE_CARD_CONTACT)
        return y + 16

    def _draw_match_reason_box(
        self,
        x: float,
        y: float,
        width: float,
        summary: str,
    ) -> float:
        c = self.c
        lines = simpleSplit(summary, s.FONT_REGULAR, s.SIZE_MATCH_BOX, width)
        box_h = 12 + len(lines) * s.SIZE_MATCH_BOX * s.LINE_HEIGHT_BODY + 8
        c.setFillColor(s.COLOR_SURFACE)
        c.roundRect(x, self.y_rl(y + box_h), width, box_h, s.CARD_RADIUS, fill=1, stroke=0)
        line_y = y + 10
        c.setFillColor(s.COLOR_TEXT_MUTED)
        c.setFont(s.FONT_REGULAR, s.SIZE_MATCH_BOX)
        for line in lines:
            c.drawString(x + 8, self.y_rl(line_y + s.SIZE_MATCH_BOX), line)
            line_y += s.SIZE_MATCH_BOX * s.LINE_HEIGHT_BODY
        return y + box_h

    def _draw_criteria_pills(
        self,
        x: float,
        y: float,
        width: float,
        criteria: List[str],
    ) -> float:
        c = self.c
        cx = x
        cy = y
        row_h = s.SIZE_PILL + s.PILL_PAD_V * 2 + 4
        for criterion in criteria:
            c.setFont(s.FONT_BOLD, s.SIZE_PILL)
            tw = c.stringWidth(criterion, s.FONT_BOLD, s.SIZE_PILL)
            pill_w = tw + s.PILL_PAD_H * 2
            if cx + pill_w > x + width:
                cx = x
                cy += row_h
            c.setFillColor(s.COLOR_SURFACE)
            c.setStrokeColor(s.COLOR_BORDER)
            c.setLineWidth(0.5)
            c.roundRect(
                cx,
                self.y_rl(cy + row_h),
                pill_w,
                row_h,
                s.PILL_RADIUS,
                fill=1,
                stroke=1,
            )
            c.setFillColor(s.COLOR_TEXT_MUTED)
            c.drawString(cx + s.PILL_PAD_H, self.y_rl(cy + row_h - s.PILL_PAD_V - 2), criterion)
            cx += pill_w + 8
        return cy + row_h

    def _draw_gap_section(
        self,
        x: float,
        y: float,
        width: float,
        questions: list,
    ) -> float:
        c = self.c
        cur = y + 6
        c.setStrokeColor(s.COLOR_BORDER)
        c.setLineWidth(0.5)
        c.line(x, self.y_rl(cur), x + width, self.y_rl(cur))
        cur += 10

        c.setFillColor(s.COLOR_TEXT_MUTED)
        c.setFont(s.FONT_BOLD, s.SIZE_GAP_TITLE)
        c.drawString(x, self.y_rl(cur + 10), "QUESTIONS TO ASK")
        nudge = "Answering these could move this to a strong match"
        c.setFont(s.FONT_ITALIC, s.SIZE_GAP_NUDGE)
        c.drawRightString(x + width, self.y_rl(cur + 10), nudge)
        cur += 22

        for i, gq in enumerate(questions):
            q_lines = simpleSplit(gq.question, s.FONT_BOLD, s.SIZE_GAP_Q, width)
            c.setFillColor(s.COLOR_TEXT_PRIMARY)
            c.setFont(s.FONT_BOLD, s.SIZE_GAP_Q)
            for line in q_lines:
                c.drawString(x, self.y_rl(cur + s.SIZE_GAP_Q), line)
                cur += s.SIZE_GAP_Q * s.LINE_HEIGHT_BODY
            n_lines = simpleSplit(gq.note, s.FONT_REGULAR, s.SIZE_GAP_NOTE, width)
            c.setFillColor(s.COLOR_TEXT_MUTED)
            c.setFont(s.FONT_REGULAR, s.SIZE_GAP_NOTE)
            for line in n_lines:
                c.drawString(x, self.y_rl(cur + s.SIZE_GAP_NOTE), line)
                cur += s.SIZE_GAP_NOTE * s.LINE_HEIGHT_BODY
            cur += s.GAP_ITEM_PAD
            if i < len(questions) - 1:
                c.setStrokeColor(s.COLOR_BORDER)
                c.line(x, self.y_rl(cur), x + width, self.y_rl(cur))
                cur += 6
        return cur

    def _truncate(self, text: str, max_width: float, font: str, size: float) -> str:
        c = self.c
        if c.stringWidth(text, font, size) <= max_width:
            return text
        ell = "…"
        while text and c.stringWidth(text + ell, font, size) > max_width:
            text = text[:-1]
        return (text + ell) if text else ell
