"""Design system constants — single source of truth for PDF rendering."""

from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

_REPO_ROOT = Path(__file__).resolve().parents[2]
PRISM_LOGO_PATH = _REPO_ROOT / "assets" / "branding" / "PrismLogo3.png"
LOGO_HEIGHT = 32
LOGO_GAP = 10

# Fonts — ReportLab built-ins only, no external files
FONT_REGULAR = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
FONT_ITALIC = "Helvetica-Oblique"

# Brand
COLOR_ACCENT = HexColor("#6366F1")
COLOR_WHITE = HexColor("#FFFFFF")
COLOR_PAGE_BG = HexColor("#FFFFFF")

# Text
COLOR_TEXT_PRIMARY = HexColor("#1A1A1A")
COLOR_TEXT_MUTED = HexColor("#6B7280")

# Surfaces
COLOR_SURFACE = HexColor("#F3F4F6")
COLOR_BORDER = HexColor("#D1D5DB")

# Match strength badges — fill + text pairs
COLOR_STRONG_FILL = HexColor("#EEF2FF")
COLOR_STRONG_TEXT = HexColor("#4338CA")
COLOR_MEDIUM_FILL = HexColor("#FFFBEB")
COLOR_MEDIUM_TEXT = HexColor("#92400E")
COLOR_WEAK_FILL = HexColor("#F3F4F6")
COLOR_WEAK_TEXT = HexColor("#6B7280")

# Page — US Letter
PAGE_W, PAGE_H = letter
MARGIN_L = MARGIN_R = MARGIN_T = MARGIN_B = 0.75 * inch
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R

# Type sizes (points)
SIZE_PROG_NAME = 17
SIZE_EYEBROW = 8
SIZE_BRAND_NAME = 11
SIZE_BRAND_SUB = 9
SIZE_RUN_DATE = 9
SIZE_STAT_VAL = 19
SIZE_STAT_LABEL = 9
SIZE_SEC_LABEL = 8
SIZE_TABLE_HEADER = 8
SIZE_TABLE_BODY = 9
SIZE_CARD_CO = 12
SIZE_CARD_POC = 10
SIZE_CARD_CONTACT = 10
SIZE_CARD_RANK = 9
SIZE_MATCH_BOX = 10
SIZE_PILL = 8
SIZE_AE_LINE = 9
SIZE_GAP_TITLE = 8
SIZE_GAP_NUDGE = 9
SIZE_GAP_Q = 10
SIZE_GAP_NOTE = 9
SIZE_FOOTER = 8
SIZE_CONDENSED_HDR = 9
SIZE_BADGE = 8

# Spacing
STAT_CARD_H = 44
STAT_GAP = 6
ROW_H = 26
CARD_PAD = 10
CARD_RADIUS = 5
PILL_PAD_H = 7
PILL_PAD_V = 2
PILL_RADIUS = 8
GAP_ITEM_PAD = 8
SECTION_GAP = 12
LINE_HEIGHT_BODY = 1.45

# Layout helpers
FOOTER_HEIGHT = 28
LIST_HEADER_H = 20
HEADER_FULL_HEIGHT = 88
CONDENSED_HEADER_HEIGHT = 36
BADGE_COL_W = 48
RANK_COL_W = 20
GAP_AFTER_HEADER_RULE = 16
GAP_AFTER_SUMMARY = 16
SECTION_LABEL_HEIGHT = 20
GAP_AFTER_SECTION_LABEL = 16
CARD_GAP = 10
SAFETY_MARGIN = 10
