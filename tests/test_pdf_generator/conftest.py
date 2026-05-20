"""Fixtures for PDF generator tests."""

import pytest

from src.pdf_generator.models import (
    GapQuestion,
    MatchReport,
    MatchedContact,
    MatchStrength,
)


@pytest.fixture
def sample_match_report() -> MatchReport:
    """2 strong (no gaps), 2 medium (with gaps), 1 weak."""
    contacts = [
        MatchedContact(
            rank=1,
            company_name="Green Valley Farms LLC",
            point_of_contact="Maria Gonzalez",
            phone="(701) 555-0142",
            email="maria@greenvalleyfarms.com",
            location="Barnes County, ND",
            account_executive="Jordan Smith",
            match_strength=MatchStrength.STRONG,
            match_summary="Qualifying drought loss with NAP payment documented.",
            criteria_met=["Named disaster", "NAP payment"],
            gap_questions=[],
        ),
        MatchedContact(
            rank=2,
            company_name="Prairie Wind Ranch",
            point_of_contact="James Okafor",
            phone="(605) 555-0198",
            email="j.okafor@prairiewind.com",
            location="Brown County, SD",
            account_executive="Taylor Reed",
            match_strength=MatchStrength.STRONG,
            match_summary="Hurricane loss in 2024 with insurance indemnity on file.",
            criteria_met=["Named disaster", "Insurance indemnity"],
            gap_questions=[],
        ),
        MatchedContact(
            rank=3,
            company_name="Sunrise Orchards",
            point_of_contact="Linda Chen",
            phone="(509) 555-0111",
            email="linda@sunriseorchards.com",
            location="Yakima County, WA",
            account_executive="Jordan Smith",
            match_strength=MatchStrength.MEDIUM,
            match_summary="Disaster confirmed; coverage level documentation incomplete.",
            criteria_met=["Named disaster"],
            gap_questions=[
                GapQuestion(
                    question="What is the crop insurance coverage level?",
                    note="Needed for payment factor calculation.",
                )
            ],
        ),
        MatchedContact(
            rank=4,
            company_name="River Bend Produce Co.",
            point_of_contact="Robert Hayes",
            phone="(870) 555-0177",
            email="rhayes@riverbendproduce.com",
            location="Phillips County, AR",
            account_executive="Alex Morgan",
            match_strength=MatchStrength.MEDIUM,
            match_summary="Flood loss documented; AGI percentage unverified.",
            criteria_met=["Named disaster"],
            gap_questions=[
                GapQuestion(
                    question="What percentage of AGI is from farming?",
                    note="≥75% unlocks higher payment cap.",
                )
            ],
        ),
        MatchedContact(
            rank=5,
            company_name="Meadow Creek Farms",
            point_of_contact="Susan Wright",
            phone="(319) 555-0133",
            email="swright@meadowcreek.com",
            location="Johnson County, IA",
            account_executive="Taylor Reed",
            match_strength=MatchStrength.WEAK,
            match_summary="Missing insurance and citizenship verification.",
            criteria_met=["State location"],
            gap_questions=[],
        ),
    ]
    return MatchReport(
        program_name="SDRP 2023–2024",
        run_date="2026-05-20",
        total_records_evaluated=213,
        contacts=contacts,
    )
