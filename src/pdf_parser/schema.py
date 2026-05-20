"""Pydantic schema for program eligibility criteria output."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


class HardRequirement(BaseModel):
    id: str
    label: str
    description: str
    disqualifier_condition: str
    crm_field_names: list[str]


class RankingCriterion(BaseModel):
    id: str
    label: str
    tier: Literal[1, 2, 3]
    tier_rationale: str
    description: str
    crm_field_names: list[str]


class Exclusion(BaseModel):
    id: str
    category: str
    detail: str


class CriteriaObject(BaseModel):
    program_name: str
    program_type: Literal["standard", "custom"]
    extraction_date: str
    ideal_profile_summary: str
    hard_requirements: list[HardRequirement]
    ranking_criteria: list[RankingCriterion]
    exclusions: list[Exclusion]
    data_fields_required: list[str] = Field(default_factory=list)
    custom_research_needed: bool
    custom_research_output: Optional[dict]
    source_files: list[str]

    @model_validator(mode="after")
    def validate_criteria_object(self) -> CriteriaObject:
        if not self.hard_requirements:
            raise ValueError("hard_requirements must be non-empty")

        tiers = {c.tier for c in self.ranking_criteria}
        if 1 not in tiers:
            raise ValueError("ranking_criteria must contain at least one Tier 1 item")
        if 2 not in tiers:
            raise ValueError("ranking_criteria must contain at least one Tier 2 item")

        if not self.data_fields_required:
            raise ValueError("data_fields_required must be non-empty")

        if len(self.data_fields_required) != len(set(self.data_fields_required)):
            raise ValueError("data_fields_required must not contain duplicates")

        if self.custom_research_needed and self.custom_research_output is None:
            raise ValueError(
                "custom_research_output must not be None when custom_research_needed is True"
            )

        return self
