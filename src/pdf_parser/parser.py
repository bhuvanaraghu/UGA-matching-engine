"""Orchestrator for PDF program parsing pipeline."""

from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from pydantic import ValidationError

from src.pdf_parser.extractor import BasePDFExtractor, DefaultPDFExtractor
from src.pdf_parser.postprocessor import build
from src.pdf_parser.prompt_chain import PromptChain
from src.pdf_parser.schema import CriteriaObject

load_dotenv()


def _output_dir() -> Path:
    return Path(os.getenv("OUTPUT_DIR", "./outputs"))


def _write_criteria(criteria: CriteriaObject, program_name: str) -> Path:
    output_dir = _output_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    filename = f"{program_name}_criteria_{today}.json"
    output_path = output_dir / filename
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(criteria.model_dump(), fh, indent=2)
    return output_path


def parse(
    pdf_paths: list[str],
    program_name: str,
    program_type: str = "standard",
    custom_research_path: str | None = None,
    extractor: BasePDFExtractor | None = None,
    prompt_chain: PromptChain | None = None,
) -> CriteriaObject:
    """
    Run the full parse pipeline: extract → prompt chain → postprocess → validate → write.

    Returns the validated CriteriaObject. Writes JSON to outputs/.
    """
    if program_type not in ("standard", "custom"):
        raise ValueError(f"Invalid program_type: {program_type}")

    pdf_extractor = extractor or DefaultPDFExtractor()
    chain = prompt_chain or PromptChain()

    program_text = pdf_extractor.extract(pdf_paths)
    chain_result = chain.run(program_text)

    criteria = build(
        chain_result=chain_result,
        program_name=program_name,
        program_type=program_type,
        custom_research_path=custom_research_path,
        source_files=[str(Path(p).resolve()) for p in pdf_paths],
    )

    try:
        CriteriaObject.model_validate(criteria.model_dump())
    except ValidationError as exc:
        raise ValueError(f"Criteria validation failed: {exc}") from exc

    _write_criteria(criteria, program_name)
    return criteria
