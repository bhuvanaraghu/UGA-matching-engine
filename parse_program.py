#!/usr/bin/env python3
"""CLI entry point for parsing grant program PDFs into criteria JSON."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pydantic import ValidationError

from src.pdf_parser.extractor import ExtractionError
from src.pdf_parser.parser import parse


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Parse grant program PDFs and extract eligibility criteria."
    )
    parser.add_argument(
        "pdf_files",
        nargs="+",
        help="One or more PDF file paths (concatenated if multiple)",
    )
    parser.add_argument(
        "--program-name",
        help="Program label (default: stem of first PDF filename)",
    )
    parser.add_argument(
        "--program-type",
        choices=["standard", "custom"],
        default="standard",
        help="Program type: standard (default) or custom (SDRP field mapping)",
    )
    parser.add_argument(
        "--custom-research",
        dest="custom_research",
        metavar="PATH",
        help="Path to JSON or CSV custom research file (e.g. disaster events table)",
    )
    args = parser.parse_args()

    for pdf_path in args.pdf_files:
        path = Path(pdf_path)
        if not path.exists():
            print(f"Error: PDF file not found: {pdf_path}", file=sys.stderr)
            return 1
        if path.suffix.lower() != ".pdf":
            print(f"Error: Not a PDF file: {pdf_path}", file=sys.stderr)
            return 1

    program_name = args.program_name
    if not program_name:
        program_name = Path(args.pdf_files[0]).stem.upper().replace(" ", "_")

    if args.program_type == "custom" and not args.custom_research:
        print(
            "Warning: --program-type custom without --custom-research; "
            "custom_research_output will be a placeholder.",
            file=sys.stderr,
        )

    try:
        criteria = parse(
            pdf_paths=args.pdf_files,
            program_name=program_name,
            program_type=args.program_type,
            custom_research_path=args.custom_research,
        )
    except ExtractionError as exc:
        print(f"Error: PDF extraction failed — {exc}", file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except ValidationError as exc:
        print(f"Error: Validation failed — {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    import os
    from datetime import date

    output_dir = Path(os.getenv("OUTPUT_DIR", "./outputs"))
    output_name = f"{program_name}_criteria_{date.today().isoformat()}.json"
    output_path = output_dir / output_name
    print(str(output_path.resolve()))
    print(f"Program: {criteria.program_name} ({criteria.program_type})")
    print(
        f"Hard requirements: {len(criteria.hard_requirements)}, "
        f"Ranking criteria: {len(criteria.ranking_criteria)}, "
        f"Exclusions: {len(criteria.exclusions)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
