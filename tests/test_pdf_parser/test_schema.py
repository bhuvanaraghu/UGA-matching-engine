"""Tests for CriteriaObject schema validation."""

import pytest
from pydantic import ValidationError

from src.pdf_parser.schema import (
    CriteriaObject,
    Exclusion,
    HardRequirement,
    RankingCriterion,
)


def _minimal_criteria(**overrides) -> dict:
    base = {
        "program_name": "TEST",
        "program_type": "standard",
        "extraction_date": "2026-05-20",
        "ideal_profile_summary": "Ideal producer summary.",
        "hard_requirements": [
            HardRequirement(
                id="hard_1",
                label="Citizenship",
                description="Must be US citizen",
                disqualifier_condition="Not a citizen",
                crm_field_names=["citizenship_status"],
            )
        ],
        "ranking_criteria": [
            RankingCriterion(
                id="rank_1",
                label="Insurance",
                tier=1,
                tier_rationale="Strong signal",
                description="Has insurance",
                crm_field_names=["insurance_or_nap_coverage_2023_2024"],
            ),
            RankingCriterion(
                id="rank_2",
                label="Coverage level",
                tier=2,
                tier_rationale="Moderate signal",
                description="Coverage level",
                crm_field_names=["type_of_crop_insurance_2024_2023"],
            ),
        ],
        "exclusions": [
            Exclusion(id="ex_1", category="Block grant", detail="CT, HI, ME, MA")
        ],
        "data_fields_required": [
            "citizenship_status",
            "insurance_or_nap_coverage_2023_2024",
        ],
        "custom_research_needed": False,
        "custom_research_output": None,
        "source_files": ["uploads/test.pdf"],
    }
    base.update(overrides)
    return base


def test_valid_criteria_object():
    obj = CriteriaObject(**_minimal_criteria())
    assert obj.program_name == "TEST"
    assert len(obj.hard_requirements) == 1


def test_rejects_empty_hard_requirements():
    data = _minimal_criteria(hard_requirements=[])
    with pytest.raises(ValidationError, match="hard_requirements"):
        CriteriaObject(**data)


def test_rejects_missing_tier_1():
    data = _minimal_criteria(
        ranking_criteria=[
            RankingCriterion(
                id="rank_2",
                label="Only tier 2",
                tier=2,
                tier_rationale="Moderate",
                description="Desc",
                crm_field_names=["field_a"],
            )
        ]
    )
    with pytest.raises(ValidationError, match="Tier 1"):
        CriteriaObject(**data)


def test_rejects_duplicate_data_fields():
    data = _minimal_criteria(
        data_fields_required=["citizenship_status", "citizenship_status"]
    )
    with pytest.raises(ValidationError, match="duplicate"):
        CriteriaObject(**data)


def test_requires_custom_research_output_when_needed():
    data = _minimal_criteria(
        custom_research_needed=True,
        custom_research_output=None,
    )
    with pytest.raises(ValidationError, match="custom_research_output"):
        CriteriaObject(**data)
