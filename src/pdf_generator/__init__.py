"""PDF output generator for ranked client match reports."""

from src.pdf_generator.generator import generate, PageManager
from src.pdf_generator.models import (
    GapQuestion,
    MatchReport,
    MatchedContact,
    MatchStrength,
)

__all__ = [
    "generate",
    "PageManager",
    "GapQuestion",
    "MatchReport",
    "MatchedContact",
    "MatchStrength",
]
