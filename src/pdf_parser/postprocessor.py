"""Parse prompt chain outputs and assemble CriteriaObject."""

from __future__ import annotations

import csv
import json
import re
from datetime import date
from pathlib import Path

from src.pdf_parser.prompt_chain import PromptChainResult
from src.pdf_parser.schema import (
    CriteriaObject,
    Exclusion,
    HardRequirement,
    RankingCriterion,
)

# Zoho CRM Farms module field names (snake_case), per docs/ZOHO_CRM_DATA_ANALYSIS.md
SDRP_FIELD_MAP: dict[str, list[str]] = {
    "citizenship": ["citizenship_status"],
    "ownership_share": ["entity_members", "producer_role"],
    "disaster_event_type": ["loss_cause_2023_2024"],
    "disaster_event_year": ["loss_payments_year_s"],
    "farm_state_county": ["farm_state", "county"],
    "block_grant_exclusion": ["ct_hi_me_ma_losses"],
    "insurance_coverage_level": ["type_of_crop_insurance_2024_2023"],
    "stage1_insurance": ["insurance_or_nap_coverage_2023_2024"],
    "specialty_crop_flag": ["what_they_produce", "farm_grows_produces_specialty_crops"],
    "agi_farming_pct": ["agi_900k_75_farm_income"],
    "trees_vines_bushes": ["losses_crops_trees_vines_2023_2024"],
    "ad1026_compliance": ["ad1026_on_file"],
    "erp_duplicate": ["erp_2022_payment_history"],
    "elap_duplicate": ["elap_payment_history"],
    "ccid": ["account_test"],
}

SDRP_LABEL_KEYWORDS: dict[str, list[str]] = {
    "citizenship": ["citizen", "residen", "us person"],
    "ownership_share": ["ownership", "share", "at risk", "producer role"],
    "disaster_event_type": ["disaster", "loss cause", "named disaster", "wildfire", "hurricane", "flood", "drought", "tornado"],
    "disaster_event_year": ["2023", "2024", "disaster year", "loss year"],
    "farm_state_county": ["state", "county", "location", "geographic"],
    "block_grant_exclusion": [
        "block grant",
        "not located in block grant",
        "connecticut",
        "hawaii",
        "maine",
        "massachusetts",
        " ct ",
        " hi ",
        " me ",
        " ma ",
    ],
    "insurance_coverage_level": ["coverage level", "insurance level", "policy level"],
    "stage1_insurance": ["insurance", "nap", "indemnity", "stage 1"],
    "specialty_crop_flag": ["specialty", "high-value crop", "commodity"],
    "agi_farming_pct": ["agi", "adjusted gross income", "farm income", "75%"],
    "trees_vines_bushes": ["tree", "vine", "bush", "orchard"],
    "ad1026_compliance": ["ad-1026", "ad1026", "conservation compliance"],
    "erp_duplicate": ["erp", "2022"],
    "elap_duplicate": ["elap"],
}


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug[:80] if slug else "criterion"


def _to_snake_case(name: str) -> str:
    name = name.strip()
    name = re.sub(r"[^\w\s]", "", name)
    return _slugify(name.replace(" ", "_"))


def _parse_numbered_items(text: str) -> list[str]:
    items: list[str] = []
    current: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"^\d+[\.\)]\s+", stripped):
            if current:
                items.append(" ".join(current).strip())
            current = [re.sub(r"^\d+[\.\)]\s+", "", stripped)]
        elif stripped and current:
            current.append(stripped)
        elif stripped and not current:
            current = [stripped]
    if current:
        items.append(" ".join(current).strip())
    return [item for item in items if item]


def _split_sections(text: str, labels: list[str]) -> dict[str, str]:
    pattern = "|".join(re.escape(label) for label in labels)
    parts = re.split(rf"(?i)(?:^|\n)\s*(?:{pattern})\s*:?\s*", text)
    if len(parts) <= 1:
        return {}
    sections: dict[str, str] = {}
    for i, label in enumerate(labels):
        idx = i + 1
        if idx < len(parts):
            sections[label.lower()] = parts[idx].strip()
    return sections


def _parse_hard_and_variable(p3_text: str) -> tuple[list[str], list[str]]:
    sections = _split_sections(
        p3_text,
        [
            "HARD PASS/FAIL",
            "HARD PASS",
            "VARIABLE FACTOR",
            "VARIABLE FACTORS",
        ],
    )
    hard_text = (
        sections.get("hard pass/fail", "")
        or sections.get("hard pass", "")
        or ""
    )
    variable_text = (
        sections.get("variable factor", "")
        or sections.get("variable factors", "")
        or ""
    )

    if not hard_text and not variable_text:
        hard_text, variable_text = p3_text, ""

    hard_items = _parse_numbered_items(hard_text) if hard_text else []
    variable_items = _parse_numbered_items(variable_text) if variable_text else []

    if not hard_items and not variable_items:
        lines = [ln.strip() for ln in p3_text.splitlines() if ln.strip()]
        for line in lines:
            lower = line.lower()
            if "variable" in lower and "hard" not in lower:
                continue
            if "hard" in lower or "pass/fail" in lower:
                hard_items.append(re.sub(r"^[\-\*]\s*", "", line))
            elif "variable" in lower or "tier" in lower:
                variable_items.append(re.sub(r"^[\-\*]\s*", "", line))

    return hard_items, variable_items


def _parse_field_mappings(p4_text: str) -> dict[str, list[str]]:
    mappings: dict[str, list[str]] = {}
    for line in p4_text.splitlines():
        line = line.strip()
        if not line:
            continue
        match = re.match(
            r"^(?:\d+[\.\)]\s*)?(.+?)\s*(?:→|->|:)\s*(.+)$",
            line,
        )
        if not match:
            continue
        criterion = match.group(1).strip()
        fields_raw = match.group(2).strip()
        fields = [
            _to_snake_case(f.strip())
            for f in re.split(r"[,;]", fields_raw)
            if f.strip()
        ]
        if criterion and fields:
            mappings[_slugify(criterion)] = fields
            mappings[criterion.lower()] = fields
    return mappings


def _parse_tier_assignments(p5_text: str) -> dict[str, tuple[int, str]]:
    assignments: dict[str, tuple[int, str]] = {}
    current_tier: int | None = None

    for line in p5_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        tier_match = re.match(r"^tier\s*(\d)", stripped, re.IGNORECASE)
        if tier_match:
            current_tier = int(tier_match.group(1))
            continue
        if current_tier is None:
            continue
        item_match = re.match(r"^(?:\d+[\.\)\-]\s*|\-\s*)(.+)$", stripped)
        item_text = item_match.group(1) if item_match else stripped
        rationale = ""
        if " — " in item_text:
            item_text, rationale = item_text.split(" — ", 1)
        elif " - " in item_text and ": " not in item_text[:30]:
            parts = item_text.split(" - ", 1)
            if len(parts) == 2 and len(parts[1]) > 20:
                item_text, rationale = parts
        key = _slugify(item_text)
        assignments[key] = (current_tier, rationale.strip() or f"Assigned to Tier {current_tier}.")
        assignments[item_text.lower()] = assignments[key]

    return assignments


def _parse_exclusions(p2_text: str) -> list[Exclusion]:
    exclusions: list[Exclusion] = []
    for idx, item in enumerate(_parse_numbered_items(p2_text), start=1):
        category = item
        detail = item
        if " — " in item:
            category, detail = item.split(" — ", 1)
        elif ": " in item:
            category, detail = item.split(": ", 1)
        exclusions.append(
            Exclusion(
                id=f"exclusion_{idx}",
                category=category.strip(),
                detail=detail.strip(),
            )
        )
    return exclusions


def _lookup_fields(
    label: str,
    field_mappings: dict[str, list[str]],
    program_type: str,
) -> list[str]:
    label_lower = label.lower()
    slug = _slugify(label)

    for key, fields in field_mappings.items():
        if key in label_lower or label_lower in key:
            return list(fields)

    if program_type == "custom":
        for map_key, keywords in SDRP_LABEL_KEYWORDS.items():
            if any(kw in label_lower for kw in keywords):
                return list(SDRP_FIELD_MAP.get(map_key, []))

    extracted: list[str] = []
    tokens = re.findall(r"[a-z][a-z0-9_]{2,}", label_lower)
    for token in tokens:
        if token not in extracted:
            extracted.append(token)
    return extracted[:3] if extracted else ["unknown_field"]


def _apply_sdrp_map(fields: list[str], label: str) -> list[str]:
    label_lower = label.lower()
    for map_key, keywords in SDRP_LABEL_KEYWORDS.items():
        if any(kw in label_lower for kw in keywords):
            mapped = SDRP_FIELD_MAP.get(map_key, [])
            if mapped:
                merged = list(dict.fromkeys(mapped + fields))
                return merged
    return fields


def _normalize_fields(fields: list[str], program_type: str, label: str) -> list[str]:
    normalized = [_to_snake_case(f) for f in fields if f]
    if program_type == "custom":
        normalized = _apply_sdrp_map(normalized, label)
    return list(dict.fromkeys(normalized)) or ["unknown_field"]


def _build_hard_requirements(
    hard_items: list[str],
    field_mappings: dict[str, list[str]],
    program_type: str,
) -> list[HardRequirement]:
    requirements: list[HardRequirement] = []
    for idx, item in enumerate(hard_items, start=1):
        label = item
        description = item
        disqualifier = f"Producer does not meet: {item}"
        if " — " in item:
            label, description = item.split(" — ", 1)
        elif ": " in item:
            parts = item.split(": ", 1)
            if len(parts[0]) < 80:
                label, description = parts

        fields = _lookup_fields(label, field_mappings, program_type)
        fields = _normalize_fields(fields, program_type, label)

        requirements.append(
            HardRequirement(
                id=f"hard_{idx}",
                label=label.strip(),
                description=description.strip(),
                disqualifier_condition=disqualifier.strip(),
                crm_field_names=fields,
            )
        )
    return requirements


def _build_ranking_criteria(
    variable_items: list[str],
    tier_assignments: dict[str, tuple[int, str]],
    field_mappings: dict[str, list[str]],
    program_type: str,
) -> list[RankingCriterion]:
    criteria: list[RankingCriterion] = []
    for idx, item in enumerate(variable_items, start=1):
        label = item
        description = item
        tier = 2
        rationale = "Moderate indicator based on program variable factor."

        if " — " in item:
            label, description = item.split(" — ", 1)

        slug = _slugify(label)
        for key, (t, r) in tier_assignments.items():
            if key in slug or slug in key or key in label.lower():
                tier = t
                rationale = r
                break

        fields = _lookup_fields(label, field_mappings, program_type)
        fields = _normalize_fields(fields, program_type, label)

        criteria.append(
            RankingCriterion(
                id=f"rank_{idx}",
                label=label.strip(),
                tier=tier,  # type: ignore[arg-type]
                tier_rationale=rationale,
                description=description.strip(),
                crm_field_names=fields,
            )
        )
    return criteria


def _collect_data_fields(
    hard: list[HardRequirement],
    ranking: list[RankingCriterion],
) -> list[str]:
    fields: list[str] = []
    for req in hard:
        fields.extend(req.crm_field_names)
    for crit in ranking:
        fields.extend(crit.crm_field_names)
    return list(dict.fromkeys(f for f in fields if f))


def _load_custom_research(path: str | None) -> dict | None:
    if not path:
        return None
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Custom research file not found: {path}")

    suffix = file_path.suffix.lower()
    if suffix == ".json":
        with file_path.open(encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            return {"records": data}
        return data

    if suffix == ".csv":
        with file_path.open(encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            rows = list(reader)
        return {"records": rows, "format": "csv"}

    raise ValueError(
        f"Unsupported custom research file format '{suffix}'. Use .json or .csv."
    )


def build(
    chain_result: PromptChainResult,
    program_name: str,
    program_type: str,
    custom_research_path: str | None = None,
    source_files: list[str] | None = None,
) -> CriteriaObject:
    """Assemble a CriteriaObject from raw prompt chain outputs."""
    hard_items, variable_items = _parse_hard_and_variable(chain_result.p3)
    field_mappings = _parse_field_mappings(chain_result.p4)
    tier_assignments = _parse_tier_assignments(chain_result.p5)
    exclusions = _parse_exclusions(chain_result.p2)

    hard_requirements = _build_hard_requirements(
        hard_items, field_mappings, program_type
    )
    ranking_criteria = _build_ranking_criteria(
        variable_items, tier_assignments, field_mappings, program_type
    )

    if not hard_requirements:
        fallback_items = _parse_numbered_items(chain_result.p1)[:5]
        hard_requirements = _build_hard_requirements(
            fallback_items, field_mappings, program_type
        )

    if not ranking_criteria:
        ranking_criteria = [
            RankingCriterion(
                id="rank_default_1",
                label="Insurance or NAP coverage",
                tier=1,
                tier_rationale="Primary Stage 1 eligibility signal.",
                description="Producer received crop insurance indemnity or NAP payment.",
                crm_field_names=_normalize_fields(
                    ["insurance_or_nap_coverage_2023_2024"],
                    program_type,
                    "insurance",
                ),
            ),
            RankingCriterion(
                id="rank_default_2",
                label="Disaster event documentation",
                tier=2,
                tier_rationale="Influences payment size and qualification confidence.",
                description="Named qualifying disaster event in 2023 or 2024.",
                crm_field_names=_normalize_fields(
                    ["loss_cause_2023_2024"],
                    program_type,
                    "disaster",
                ),
            ),
        ]

    custom_research_needed = program_type == "custom"
    custom_research_output = _load_custom_research(custom_research_path)

    if custom_research_needed and custom_research_output is None:
        custom_research_output = {"status": "pending", "note": "No research file provided"}

    data_fields_required = _collect_data_fields(hard_requirements, ranking_criteria)

    if program_type == "custom":
        for fields in SDRP_FIELD_MAP.values():
            for field in fields:
                if field not in data_fields_required:
                    data_fields_required.append(field)

    return CriteriaObject(
        program_name=program_name,
        program_type=program_type,  # type: ignore[arg-type]
        extraction_date=date.today().isoformat(),
        ideal_profile_summary=chain_result.p6.strip(),
        hard_requirements=hard_requirements,
        ranking_criteria=ranking_criteria,
        exclusions=exclusions,
        data_fields_required=data_fields_required,
        custom_research_needed=custom_research_needed,
        custom_research_output=custom_research_output,
        source_files=source_files or [],
    )
