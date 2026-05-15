# Amanda Coordination - Format Alignment
## Matching Engine Integration

**Date:** May 12, 2026
**Status:** Amanda's SDRP criteria extraction COMPLETE ✅
**Next Step:** Align format for matching engine consumption

---

## What Amanda Has Already Built ✅

Amanda created: **"SDRP Eligibility Criteria - Matching & Ranking Framework for CRM Field Mapping"**

This document includes:
- ✅ Hard requirements (pass/fail)
- ✅ Tier 1 strong indicators
- ✅ Tier 2 moderate indicators
- ✅ Tier 3 supporting details
- ✅ CRM field mapping checklist (Section 5)
- ✅ Ineligibility & exclusion rules

**This is exactly what we need!** Amanda has done her part.

---

## Format Alignment Needed

Amanda's output is currently in **Markdown/narrative format**.
The matching engine needs **structured JSON**.

### Two Options:

**Option A: Amanda Converts to JSON** (Recommended)
- Amanda takes her existing criteria document
- Structures it as JSON using the format in `AMANDA_HANDOFF.md`
- Delivers: `sdrp_criteria.json`
- **Effort:** 2-3 hours

**Option B: Matching Engine Reads Markdown** (Alternative)
- Matching engine uses Claude to parse Amanda's document at runtime
- Extract criteria on-the-fly
- **Effort:** 1-2 hours (build parser)
- **Cost:** Slightly higher API cost per run

**Recommendation:** Go with Option A - cleaner, faster, cacheable

---

## Simplified Coordination Steps

### Step 1: Bhuvana Sends Amanda the Output Format

**Send Amanda:**
1. ✅ `AMANDA_HANDOFF.md` (the detailed spec I just created)
2. ✅ `ZOHO_CRM_DATA_ANALYSIS.md` (so she can verify field names)

**Ask Amanda to:**
- Review the JSON structure in `AMANDA_HANDOFF.md`
- Convert her existing criteria markdown into that JSON format
- Verify all `crm_field` names match actual Zoho fields (from data analysis doc)

---

### Step 2: Amanda Delivers Structured JSON

**File:** `sdrp_criteria.json`

**Structure:**
```json
{
  "program_name": "SDRP",
  "program_year": "2023-2024",
  "hard_requirements": [
    {
      "name": "geographic_exclusion",
      "description": "Not in block grant states (CT, HI, ME, MA)",
      "crm_field": "Farm_State",
      "excluded_values": ["CT", "HI", "ME", "MA"],
      "weight": "critical",
      "missing_data_action": "exclude"
    },
    // ... all hard requirements from her doc
  ],
  "tier_1_indicators": [
    {
      "name": "stage_1_insurance_indemnity",
      "description": "Received insurance indemnity or NAP payment (Stage 1)",
      "crm_field": "Insurance_or_NAP_Coverage_2023_2024",
      "weight": "high",
      "points": 10
    },
    // ... all Tier 1 from her doc
  ],
  "tier_2_indicators": [ /* ... */ ],
  "tier_3_requirements": [ /* ... */ ]
}
```

**She already has all the content** - just needs to structure it!

---

### Step 3: Validate Field Mappings

**Critical Check:** Verify every `crm_field` Amanda specifies exists in Zoho.

**From her document Section 5 (CRM Field Mapping Checklist), she needs to confirm:**

| Her Criteria Field | Actual Zoho Field | Exists? | Fill Rate |
|-------------------|-------------------|---------|-----------|
| Citizenship / Residency Status | ❌ Does not exist | NO | 0% → Flag for manual review |
| Ownership Share & Risk | `Entity_Members` | YES | 34.7% → Unstructured text |
| State & County | `Farm_State`, `County` | YES | 100%, 61% |
| Disaster Event Type | `Loss_Cause_2023_2024` | YES | 58.7% |
| Disaster Event Year | `Loss_Payments_Year_s` | YES | 58.7% |
| Stage 1 - Insurance Indemnity | `Insurance_or_NAP_Coverage_2023_2024` | YES | 52.6% |
| Commodity / Crop Type | `What_They_Produce` | YES | 59.6% |
| Specialty Crop Flag | `Farm_Grows_Produces_Specialty_crops` | YES | 100% (in Accounts) |
| Crop Insurance Coverage Level | `Type_of_Crop_Insurance_2024_2023` | YES | 58.7% (type only, not %) |
| AGI from Farming (%) | `AGI_900K_75_Farm_Income` | YES | 31.5% |
| Trees/Vines/Bushes | `Losses_Crops_Trees_Vines_2023_2024` | YES | 48.4% |
| AD-1026 Conservation Compliance | ❌ Does not exist | NO | 0% → Flag for manual review |
| ERP 2022 Payment History | ❌ Does not exist | NO | 0% → Flag for manual review |

**For fields that DON'T exist:**
Amanda should still include them in JSON, but set:
```json
{
  "name": "citizenship",
  "crm_field": "Citizenship_Status",
  "missing_data_action": "flag_for_manual_review"
}
```

This tells the matching engine: "We need this data, but it's not in CRM, so flag these clients for manual verification."

---

### Step 4: Test Alignment

Once Amanda delivers `sdrp_criteria.json`:

1. **Validate JSON syntax:**
   ```bash
   python -m json.tool sdrp_criteria.json
   ```

2. **Check field names:**
   - Every `crm_field` should match Zoho exactly (case-sensitive!)
   - Cross-reference with `ZOHO_CRM_DATA_ANALYSIS.md` Appendix A

3. **Verify completeness:**
   - All criteria from her markdown doc are in the JSON
   - Nothing lost in translation

4. **Test with 1 sample client:**
   - Pick one farm from Zoho
   - Manually evaluate against her JSON criteria
   - Confirm logic makes sense

---

## What the Matching Engine Will Do With Her Output

```
sdrp_criteria.json (Amanda's output)
          ↓
   [ Matching Engine ]
          ↓
   For each of 213 clients:
   1. Check hard requirements → Pass/Fail
   2. Count Tier 1 matches → Sum points
   3. Count Tier 2 matches → Sum points
   4. Calculate confidence score → 0-100
   5. Generate match rationale → "Why they qualify"
          ↓
   Ranked list → PDF → Email to Elias
```

**Amanda's criteria = the scoring rubric for the entire matching process.**

---

## Timeline

| Task | Owner | Effort | Deadline |
|------|-------|--------|----------|
| Send Amanda the format specs | Bhuvana | 5 min | Today |
| Convert criteria to JSON | Amanda | 2-3 hrs | 2 days |
| Validate JSON & field mappings | Bhuvana | 30 min | 3 days |
| Build matching engine using JSON | TBD | 23 hrs | Phase 2 |

---

## Communication Template for Amanda

**Subject:** SDRP Criteria - Format Conversion Needed for Matching Engine

Hi Amanda,

Great work on the SDRP eligibility criteria extraction! Your document has everything we need.

To integrate with the matching engine, we need your criteria in structured JSON format so the system can automatically evaluate clients.

**What I need from you:**
1. Review the output format specification in: `docs/AMANDA_HANDOFF.md`
2. Convert your existing criteria into that JSON structure
3. Verify field names against: `docs/ZOHO_CRM_DATA_ANALYSIS.md` (Appendix A)
4. Deliver: `sdrp_criteria.json`

**You already have all the content** - this is just reformatting your excellent work into machine-readable JSON. Estimated 2-3 hours.

**Key points:**
- Use exact Zoho field names (e.g., `Loss_Cause_2023_2024`, not `Disaster_Event`)
- For fields that don't exist in CRM (citizenship, AD-1026), still include them but set `missing_data_action: "flag_for_manual_review"`
- Assign point values to Tier 1 (8-10) and Tier 2 (3-6) based on strength

**Questions?** Let's sync - happy to walk through the format together.

Thanks!
Bhuvana

---

**Attachments:**
- `AMANDA_HANDOFF.md` (detailed format spec with examples)
- `ZOHO_CRM_DATA_ANALYSIS.md` (Zoho field reference)

---

## Summary

✅ **Amanda has done the hard work** (extracting criteria from SDRP PDF)
🔄 **Format alignment needed** (markdown → JSON)
⏱️ **2-3 hours for Amanda** to structure existing content as JSON
🚀 **Then matching engine can consume it** and process 213 clients

**No coordination complexity** - just a straightforward format conversion!

---

**Document Version:** 1.0
**Date:** May 12, 2026
**Next Action:** Send Amanda the format spec + field mapping reference
