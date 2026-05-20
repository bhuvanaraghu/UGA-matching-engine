"""PDF text extraction with pluggable extractor strategy."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
import re


class ExtractionError(Exception):
    """Raised when PDF text extraction fails."""


class BasePDFExtractor(ABC):
    @abstractmethod
    def extract(self, paths: list[str]) -> str:
        """Extract and concatenate text from one or more PDF files."""
        ...


class DefaultPDFExtractor(BasePDFExtractor):
    """Default extractor using pdfplumber (imported only inside this class)."""

    def extract(self, paths: list[str]) -> str:
        if not paths:
            raise ExtractionError("No PDF paths provided")

        try:
            import pdfplumber
        except ImportError as exc:
            raise ExtractionError(
                "pdfplumber is required for PDF extraction. "
                "Install it with: pip install pdfplumber"
            ) from exc

        sections: list[str] = []

        for path_str in paths:
            path = Path(path_str)
            if not path.exists():
                raise ExtractionError(f"PDF file not found: {path}")

            if path.suffix.lower() != ".pdf":
                raise ExtractionError(f"Not a PDF file: {path}")

            try:
                file_sections: list[str] = []
                with pdfplumber.open(path) as pdf:
                    for page_num, page in enumerate(pdf.pages, start=1):
                        text = page.extract_text() or ""
                        file_sections.append(
                            f"--- {path.name} | page {page_num} ---\n{text}".strip()
                        )
                combined = "\n".join(file_sections)
                if not re.sub(r"---.*?---", "", combined, flags=re.DOTALL).strip():
                    raise ExtractionError(f"No text extracted from PDF: {path}")
                sections.append(
                    f"===== FILE: {path.name} =====\n" + "\n\n".join(file_sections)
                )
            except ExtractionError:
                raise
            except Exception as exc:
                raise ExtractionError(f"Failed to read PDF '{path}': {exc}") from exc

        return "\n\n".join(sections)
