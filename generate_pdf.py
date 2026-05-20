#!/usr/bin/env python3
"""CLI entry point for generating branded match report PDFs."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from pydantic import ValidationError

from src.pdf_generator.generator import generate
from src.pdf_generator.models import MatchReport


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a branded PDF from a MatchReport JSON file."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to MatchReport JSON (matching engine output)",
    )
    parser.add_argument(
        "--output",
        help="Output PDF path (default: outputs/{program}_{date}_matches.pdf)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        return 1

    try:
        with input_path.open(encoding="utf-8") as fh:
            data = json.load(fh)
        report = MatchReport.model_validate(data)
    except json.JSONDecodeError as exc:
        print(f"Error: Invalid JSON — {exc}", file=sys.stderr)
        return 1
    except ValidationError as exc:
        print(f"Error: Invalid MatchReport schema — {exc}", file=sys.stderr)
        return 1

    if args.output:
        output_path = Path(args.output)
    else:
        safe_name = report.program_name.replace(" ", "_").replace("/", "-")
        output_path = Path("outputs") / f"{safe_name}_{report.run_date}_matches.pdf"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        result = generate(report, str(output_path))
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Error: PDF generation failed — {exc}", file=sys.stderr)
        return 1

    print(result)
    print(
        f"Generated PDF for {report.program_name}: "
        f"{len(report.contacts)} contacts "
        f"({len(report.strong)} strong, {len(report.medium)} medium, "
        f"{len(report.weak)} weak)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
