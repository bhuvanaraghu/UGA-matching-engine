"""Tests for MatchReport input models."""

import pytest
from pydantic import ValidationError

from src.pdf_generator.models import (
    GapQuestion,
    MatchReport,
    MatchedContact,
    MatchStrength,
)


def _contact(strength: MatchStrength, rank: int, gaps=None) -> MatchedContact:
    return MatchedContact(
        rank=rank,
        company_name="Test Farm",
        point_of_contact="Jane Doe",
        match_strength=strength,
        match_summary="Test summary.",
        gap_questions=gaps or [],
    )


def test_strength_partition_properties(sample_match_report):
    assert len(sample_match_report.strong) == 2
    assert len(sample_match_report.medium) == 2
    assert len(sample_match_report.weak) == 1


def test_empty_gap_questions_valid():
    contact = _contact(MatchStrength.STRONG, 1, gaps=[])
    assert contact.gap_questions == []


def test_rejects_invalid_match_strength():
    with pytest.raises(ValidationError):
        MatchedContact(
            rank=1,
            company_name="Farm",
            point_of_contact="POC",
            match_strength="invalid",
            match_summary="Summary",
        )


def test_empty_contacts_list_valid():
    report = MatchReport(
        program_name="TEST",
        run_date="2026-05-20",
        total_records_evaluated=0,
        contacts=[],
    )
    assert report.contacts == []
