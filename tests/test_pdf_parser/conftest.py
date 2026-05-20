"""Shared fixtures for PDF parser tests."""

import json

import pytest

from src.pdf_parser.prompt_chain import PromptChainResult


@pytest.fixture
def sdrp_prompt_chain_result() -> PromptChainResult:
    """Representative SDRP outputs from program document discovery (NotebookLM-style)."""
    return PromptChainResult(
        p1=(
            "1. Producer must be a U.S. citizen or resident alien.\n"
            "2. Producer must have an ownership share and be at risk in farming operations.\n"
            "3. Farm must be located in a state and county affected by a named qualifying "
            "disaster event in 2023 or 2024.\n"
            "4. Producer must have suffered a qualifying loss from a named disaster "
            "(wildfire, hurricane, flood, derecho, tornado, drought, etc.).\n"
            "5. Producer must not be in Connecticut, Hawaii, Maine, or Massachusetts "
            "(block grant states).\n"
            "6. Producer must have crop insurance or NAP coverage and received indemnity "
            "or NAP payment (Stage 1).\n"
            "7. Producer must maintain conservation compliance (AD-1026) on file with FSA.\n"
            "8. Producer must not have received duplicate benefits under ERP 2022 or ELAP.\n"
            "9. Producer must agree to future crop insurance linkage where applicable.\n"
            "10. Producer must have verifiable production records and FSA forms current."
        ),
        p2=(
            "1. Block grant state producers — operations primarily in CT, HI, ME, or MA.\n"
            "2. Producers without qualifying named disaster loss in 2023-2024.\n"
            "3. Producers who received duplicate ERP 2022 or ELAP benefits for the same loss.\n"
            "4. Non-citizen or non-resident alien producers.\n"
            "5. Producers not actively engaged in farming or without share at risk."
        ),
        p3=(
            "HARD PASS/FAIL:\n"
            "1. U.S. citizenship or resident alien status.\n"
            "2. Ownership share and at-risk status in farming operations.\n"
            "3. Farm located in qualifying disaster-affected state and county.\n"
            "4. Named qualifying disaster event loss in 2023 or 2024.\n"
            "5. Not located in block grant states (CT, HI, ME, MA).\n"
            "6. Conservation compliance AD-1026 on file.\n"
            "7. No duplicate ERP 2022 or ELAP benefits.\n\n"
            "VARIABLE FACTOR:\n"
            "1. Stage 1 crop insurance indemnity or NAP payment received.\n"
            "2. Crop insurance coverage level percentage.\n"
            "3. AGI at least 75% from farming operations.\n"
            "4. Tree, bush, or vine losses for specialty payments.\n"
            "5. High-disaster-impact county designation.\n"
            "6. Specialty or high-value crop production."
        ),
        p4=(
            "1. U.S. citizenship → citizenship_status\n"
            "2. Ownership share at risk → ownership_share_pct, producer_role\n"
            "3. State and county location → farm_state, farm_county\n"
            "4. Named disaster event type → disaster_event_type\n"
            "5. Disaster year 2023/2024 → disaster_event_year\n"
            "6. Block grant state exclusion → block_grant_exclusion\n"
            "7. Stage 1 insurance/NAP payment → stage1_insurance\n"
            "8. Insurance coverage level → insurance_coverage_level\n"
            "9. AGI from farming ≥75% → agi_farming_pct\n"
            "10. Tree/vine/bush losses → trees_vines_bushes\n"
            "11. AD-1026 compliance → ad1026_compliance\n"
            "12. ERP 2022 duplicate check → erp_duplicate\n"
            "13. ELAP duplicate check → elap_duplicate"
        ),
        p5=(
            "Tier 1\n"
            "1. Stage 1 crop insurance indemnity or NAP payment — primary Stage 1 "
            "eligibility driver.\n"
            "2. Named qualifying disaster event — core program qualification signal.\n\n"
            "Tier 2\n"
            "3. Crop insurance coverage level — significantly affects payment factor.\n"
            "4. AGI at least 75% from farming — influences payment cap calculation.\n"
            "5. Tree, bush, or vine losses — affects specialty payment eligibility.\n\n"
            "Tier 3\n"
            "6. FSA forms and production records current — administrative supporting detail."
        ),
        p6=(
            "The ideal SDRP match is a U.S. citizen producer with documented ownership and "
            "at-risk status, farming in a 2023-2024 named disaster-affected county outside "
            "CT, HI, ME, and MA. They suffered a qualifying wildfire, hurricane, flood, or "
            "drought loss, received crop insurance or NAP indemnity (Stage 1), maintain "
            "AD-1026 compliance, and have current FSA documentation without duplicate ERP "
            "or ELAP benefits."
        ),
    )


@pytest.fixture
def sample_disaster_events_json(tmp_path):
    """Minimal disaster events research file for custom program tests."""
    data = {
        "title": "2023-2024 Named natural disaster events",
        "records": [
            {
                "city": "Valley City",
                "state": "ND",
                "country": "USA",
                "event_name": "Drought",
                "duration": "2023",
                "reference": "https://example.com/drought-nd-2023",
            }
        ],
    }
    path = tmp_path / "disaster_events_2023_2024.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path
