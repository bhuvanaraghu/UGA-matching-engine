"""Tests for postprocessor assembly and SDRP field mapping."""

from src.pdf_parser.postprocessor import build
from src.pdf_parser.schema import CriteriaObject


def test_sdrp_build_produces_valid_criteria(
    sdrp_prompt_chain_result, sample_disaster_events_json
):
    criteria = build(
        chain_result=sdrp_prompt_chain_result,
        program_name="SDRP",
        program_type="custom",
        custom_research_path=str(sample_disaster_events_json),
        source_files=["uploads/SDRP_program_doc.pdf"],
    )

    assert isinstance(criteria, CriteriaObject)
    assert len(criteria.hard_requirements) > 0

    tiers = {c.tier for c in criteria.ranking_criteria}
    assert 1 in tiers
    assert 2 in tiers

    assert "ct_hi_me_ma_losses" in criteria.data_fields_required

    assert criteria.custom_research_needed is True
    assert criteria.custom_research_output is not None
    assert "records" in criteria.custom_research_output


def test_standard_program_uses_snake_case_fields(sdrp_prompt_chain_result):
    criteria = build(
        chain_result=sdrp_prompt_chain_result,
        program_name="GENERIC",
        program_type="standard",
        source_files=["uploads/generic.pdf"],
    )

    assert criteria.program_type == "standard"
    assert criteria.custom_research_needed is False
    assert criteria.custom_research_output is None
    assert len(criteria.data_fields_required) > 0
    assert len(criteria.data_fields_required) == len(set(criteria.data_fields_required))


def test_loads_csv_custom_research(sdrp_prompt_chain_result, tmp_path):
    csv_path = tmp_path / "events.csv"
    csv_path.write_text("city,state,event_name\nAustin,TX,Flood\n", encoding="utf-8")

    criteria = build(
        chain_result=sdrp_prompt_chain_result,
        program_name="SDRP",
        program_type="custom",
        custom_research_path=str(csv_path),
    )

    assert criteria.custom_research_output is not None
    assert criteria.custom_research_output.get("format") == "csv"
    assert len(criteria.custom_research_output["records"]) == 1
