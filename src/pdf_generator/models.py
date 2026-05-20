"""Input data models for PDF match report generation."""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class MatchStrength(str, Enum):
    STRONG = "strong"
    MEDIUM = "medium"
    WEAK = "weak"


class GapQuestion(BaseModel):
    question: str
    note: str


class MatchedContact(BaseModel):
    rank: int
    company_name: str
    point_of_contact: str
    phone: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    account_executive: Optional[str] = None
    match_strength: MatchStrength
    match_summary: str
    criteria_met: List[str] = Field(default_factory=list)
    gap_questions: List[GapQuestion] = Field(default_factory=list)


class MatchReport(BaseModel):
    program_name: str
    run_date: str
    total_records_evaluated: int
    contacts: List[MatchedContact]

    @property
    def strong(self) -> List[MatchedContact]:
        return [c for c in self.contacts if c.match_strength == MatchStrength.STRONG]

    @property
    def medium(self) -> List[MatchedContact]:
        return [c for c in self.contacts if c.match_strength == MatchStrength.MEDIUM]

    @property
    def weak(self) -> List[MatchedContact]:
        return [c for c in self.contacts if c.match_strength == MatchStrength.WEAK]
