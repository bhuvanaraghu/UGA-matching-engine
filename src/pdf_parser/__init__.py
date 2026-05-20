"""PDF program parser — extracts eligibility criteria from grant program PDFs."""

from src.pdf_parser.parser import parse
from src.pdf_parser.schema import CriteriaObject

__all__ = ["parse", "CriteriaObject"]
