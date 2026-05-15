# Program Criteria Extraction - Coordination Document
## For: Amanda Ford (PDF Parser Owner)

**Date:** May 12, 2026
**Project:** UGA Matching Engine - Engagement 4
**Your Role:** Extract SDRP eligibility criteria from program PDF using Claude

---

## What You're Building

You're responsible for **Step 1** of the matching engine: transforming the SDRP program PDF into structured, machine-readable eligibility criteria that the matching engine can use to evaluate clients.

**Input:** SDRP program PDF (eligibility criteria document)
**Output:** Structured JSON file with all eligibility criteria
**Consumer:** Matching engine (will use your output to evaluate 213 client profiles)

---

## Critical: Output Format Specification

The matching engine expects your criteria extraction to produce **this exact JSON structure**:

```json
{
  "program_name": "SDRP - Supplemental Disaster Relief Program",
  "program_year": "2023-2024",

  "hard_requirements": [
    {
      "name": "citizenship",
      "description": "U.S. citizen or resident alien",
      "crm_field": "Citizenship_Status",
      "expected_values": ["US Citizen", "Resident Alien"],
      "weight": "critical",
      "missing_data_action": "flag_for_manual_review"
    },
    {
      "name": "geographic_exclusion",
      "description": "Not in block grant states",
      "crm_field": "Farm_State",
      "excluded_values": ["CT", "HI", "ME", "MA"],
      "weight": "critical",
      "missing_data_action": "exclude"
    },
    {
      "name": "disaster_event_2023_2024",
      "description": "Loss caused by qualifying disaster in 2023-2024",
      "crm_field": "Loss_Cause_2023_2024",
      "qualifying_events": ["hurricane", "wildfire", "flood", "drought", "derecho", "excessive heat", "tornado", "winter storm", "freeze", "smoke exposure", "excessive moisture"],
      "weight": "critical",
      "missing_data_action": "exclude"
    }
    // ... continue for all hard requirements
  ],

  "tier_1_indicators": [
    {
      "name": "stage_1_insurance_indemnity",
      "description": "Already received insurance indemnity or NAP payment for 2023/2024",
      "crm_field": "Insurance_or_NAP_Coverage_2023_2024",
      "expected_values": ["Yes", "Received"],
      "weight": "high",
      "points": 10
    },
    {
      "name": "specialty_crop",
      "description": "Farm grows specialty crops (fruits, tree nuts, vegetables, etc.)",
      "crm_field": "Farm_Grows_Produces_Specialty_crops",
      "expected_values": [true, "Yes"],
      "weight": "high",
      "points": 8
    }
    // ... continue for all Tier 1 indicators
  ],

  "tier_2_indicators": [
    {
      "name": "agi_75_percent_farming",
      "description": "≥75% of AGI from farming",
      "crm_field": "AGI_900K_75_Farm_Income",
      "expected_values": [true, "Yes", "≥75%"],
      "weight": "medium",
      "points": 5
    }
    // ... continue for all Tier 2 indicators
  ],

  "tier_3_requirements": [
    {
      "name": "conservation_compliance",
      "description": "AD-1026 form on file",
      "crm_field": "AD_1026_On_File",
      "expected_values": [true, "Yes"],
      "weight": "low",
      "required_for_payment": true
    }
    // ... continue for all Tier 3 requirements
  ]
}
```

### Field Structure Explanation:

| Field | Required? | Description |
|-------|-----------|-------------|
| `name` | Yes | Unique identifier for this criterion (lowercase_with_underscores) |
| `description` | Yes | Human-readable explanation of the requirement |
| `crm_field` | Yes | **MUST match exact Zoho CRM field name** (see mapping table below) |
| `expected_values` | Conditional | List of values that satisfy this criterion (if applicable) |
| `excluded_values` | Conditional | List of values that disqualify (if applicable) |
| `qualifying_events` | Conditional | For disaster criteria - list of event types |
| `weight` | Yes | "critical", "high", "medium", or "low" |
| `points` | For Tiers 1-2 | Scoring weight for ranking (higher = stronger signal) |
| `missing_data_action` | For Hard Req. | "exclude", "flag_for_manual_review", or "assume_eligible" |
| `required_for_payment` | For Tier 3 | Boolean - is this administratively required? |

---

## Zoho CRM Field Mapping Reference

You **must** map criteria to actual Zoho CRM fields. Here are the available fields based on our Phase 1 data quality analysis:

### Available Fields - Farms Module (Primary Data Source)

| SDRP Criterion | Zoho CRM Field | Fill Rate | Notes |
|----------------|----------------|-----------|-------|
| **Hard Requirements** ||||
| Geographic location (state) | `Farm_State` | 100% | Perfect coverage |
| Geographic location (county) | `County` | 61% | Good but not complete |
| Block grant state exclusion | `CT_HI_ME_MA_Losses` | 58.7% | Directly tracked! |
| Disaster event type | `Loss_Cause_2023_2024` | 58.7% | Named event |
| Disaster year | `Loss_Payments_Year_s` | 58.7% | Year(s) of loss |
| Citizenship/Residency | ⚠️ **DOES NOT EXIST** | 0% | Flag for manual review |
| Conservation compliance (AD-1026) | ⚠️ **DOES NOT EXIST** | 0% | Flag for manual review |
| Ownership share at risk | `Entity_Members` | 34.7% | Unstructured text field |
| **Tier 1 Indicators** ||||
| Insurance indemnity/NAP received | `Insurance_or_NAP_Coverage_2023_2024` | 52.6% | Stage 1 signal |
| Named disaster event | `Loss_Cause_2023_2024` | 58.7% | Same as above |
| Crop insurance type | `Type_of_Crop_Insurance_2024_2023` | 58.7% | Type, not coverage % |
| Loss payment source | `Payment_Source_Losses` | 39.9% | Where payments came from |
| Specialty crop (boolean) | `Farm_Grows_Produces_Specialty_crops` (Accounts) | 100% | Yes/No flag |
| Crop/commodity type | `What_They_Produce` | 59.6% | Text field |
| **Tier 2 Indicators** ||||
| AGI ≥75% from farming | `AGI_900K_75_Farm_Income` | 31.5% | Boolean/text |
| Tree/vine/bush losses | `Losses_Crops_Trees_Vines_2023_2024` | 48.4% | Production loss |
| Crop insurance coverage level | ⚠️ **TYPE ONLY** | 58.7% | Have type, not exact % |
| **Tier 3 Requirements** ||||
| FSA forms up to date | `FSA_Forms_Up_to_Date` | 58.7% | General status |
| Production records available | `Production_Quality_Loss_Status` | 11.7% | Very limited |

### Fields That DON'T Exist (But Criteria May Require):

| SDRP Criterion | Status | What to Do |
|----------------|--------|------------|
| Citizenship/Residency status | ❌ Not in CRM | Set `missing_data_action: "flag_for_manual_review"` |
| AD-1026 conservation compliance | ❌ Not in CRM | Set `missing_data_action: "flag_for_manual_review"` |
| Exact insurance coverage % | ⚠️ Type only | Map to `Type_of_Crop_Insurance_2024_2023`, note limitation |
| Ownership share % | ⚠️ Unstructured | Map to `Entity_Members`, note extraction needed |
| ERP 2022 payment history | ❌ Not in CRM | Set `missing_data_action: "flag_for_manual_review"` |
| Customer Core ID (CCID) | ❌ Not in CRM | Set `missing_data_action: "flag_for_manual_review"` |

**Important:** If a criterion requires a field that doesn't exist in Zoho:
1. Still include it in your output
2. Set `crm_field` to a descriptive name (e.g., `"Citizenship_Status"`)
3. Set `missing_data_action: "flag_for_manual_review"`
4. The matching engine will flag these clients for manual verification

---

## How to Classify Criteria (Tier Assignment)

When extracting criteria from the SDRP PDF, classify each one:

### Hard Requirements (Binary Pass/Fail)
**Characteristics:**
- Absolute disqualifiers if not met
- Usually regulatory or legal requirements
- No exceptions allowed

**Examples from SDRP:**
- U.S. citizen or resident alien
- Not in CT, HI, ME, or MA (block grant states)
- Loss occurred in 2023 or 2024
- Caused by qualifying disaster event
- Not already compensated under ERP 2022/ELAP

**What to extract:**
- All absolute "must have" or "must not" conditions
- Exclusions and disqualifications
- Eligibility cutoffs (dates, locations, etc.)

---

### Tier 1 Indicators (Strong Qualification Signals)
**Characteristics:**
- Primary drivers of qualification
- High payment potential
- Strongest signals of eligibility

**Examples from SDRP:**
- Already received crop insurance indemnity or NAP payment (Stage 1)
- Named hurricane, wildfire, or flood event
- Ownership share at risk
- Specialty/high-value crop ($900K cap vs. $125K)

**What to extract:**
- Factors that significantly increase eligibility likelihood
- Payment cap multipliers
- Pre-qualification indicators (insurance indemnity, etc.)

**Assign points:** 8-10 for strongest signals, 5-7 for moderate

---

### Tier 2 Indicators (Moderate Signals)
**Characteristics:**
- Influence payment size but don't guarantee eligibility
- Tie-breakers between similar candidates
- Nice-to-have, not must-have

**Examples from SDRP:**
- Crop insurance coverage level (determines SDRP Factor 75-95%)
- AGI ≥75% from farming (higher payment limit exception)
- Tree/vine/bush losses (dual payment eligibility)
- Stage 2 shallow loss (below insurance deductible)

**What to extract:**
- Payment calculation factors
- Eligibility enhancements
- Special provisions or exceptions

**Assign points:** 3-6 depending on impact

---

### Tier 3 Requirements (Administrative/Documentation)
**Characteristics:**
- Required for payment processing but not eligibility determination
- Documentation and compliance items
- Don't affect match ranking

**Examples from SDRP:**
- AD-1026 conservation compliance form
- CCC-902 farm operating plan
- Verifiable production records
- Quality loss documentation
- Future insurance linkage agreement

**What to extract:**
- Forms and documents required
- Compliance checkboxes
- Administrative prerequisites

**Don't assign points** - these are binary requirements, not ranking factors

---

## Your Claude Prompt Template

Here's a suggested prompt structure for extracting criteria from the SDRP PDF:

```
You are an expert USDA grant program eligibility analyst.

Your task: Extract ALL eligibility criteria from this SDRP program document and structure them for a matching engine.

INSTRUCTIONS:

1. HARD REQUIREMENTS (Must-Have, Binary):
   Identify ALL absolute requirements that disqualify if not met:
   - Citizenship/residency rules
   - Geographic restrictions (states, counties)
   - Time period restrictions (disaster years, application deadlines)
   - Duplicate benefit exclusions
   - Conservation compliance
   - Any other "must have" or "must not" conditions

   For each, specify:
   - What Zoho CRM field should contain this data (refer to field mapping table)
   - What values satisfy the requirement
   - What happens if data is missing (exclude, flag, assume eligible)

2. TIER 1 STRONG INDICATORS (Primary Qualification Signals):
   Identify factors that strongly suggest eligibility:
   - Insurance indemnity or NAP payment received (Stage 1 pre-fill)
   - Specific disaster event types (hurricanes, wildfires, etc.)
   - Crop classification (specialty vs. other)
   - Ownership structure and at-risk share

   For each, specify:
   - Zoho CRM field name
   - Expected values
   - Point value (8-10 for strongest, 5-7 for moderate)

3. TIER 2 MODERATE INDICATORS (Payment Influencers):
   Identify factors that affect payment size or likelihood:
   - Insurance coverage level percentages
   - Income from farming percentage (AGI)
   - Type of loss (production, quality, plant damage)
   - County disaster impact level

   For each, specify:
   - Zoho CRM field name
   - Expected values
   - Point value (3-6)

4. TIER 3 ADMINISTRATIVE REQUIREMENTS:
   Identify documentation and compliance needs:
   - Forms required (AD-1026, CCC-902, FSA-510, etc.)
   - Record-keeping requirements
   - Application steps
   - Future commitments (insurance linkage)

   For each, specify:
   - What's required
   - Whether it's payment-blocking
   - Zoho CRM field (if tracked)

ZOHO CRM FIELD MAPPING:
Use these exact field names when mapping criteria:
[Include the field mapping table from above]

OUTPUT FORMAT:
Return a valid JSON object matching this structure:
[Include the JSON structure from above]

IMPORTANT NOTES:
- If a criterion requires data not in Zoho CRM, still include it but set missing_data_action appropriately
- Use exact Zoho field names from the mapping table
- Be exhaustive - extract EVERY criterion, even minor ones
- Classify carefully - hard requirements vs. indicators matters for matching logic

PROGRAM DOCUMENT:
[PDF text content here]
```

---

## Handoff Point: What Happens Next

Once you deliver the structured JSON criteria, here's what the matching engine will do:

### Step 2: Client Data Assembly
Bhuvana's Zoho CRM integration fetches all 213 farm client profiles.

### Step 3: Individual Client Matching
For each of the 213 clients, Claude evaluates:
1. **Check hard requirements:** Does client pass all hard requirements from your output?
   - If NO on any → client is ineligible
   - If UNKNOWN due to missing data → flag for manual review
2. **Count Tier 1 indicators:** How many Tier 1 criteria does client meet?
   - Sum up points from matched criteria
3. **Count Tier 2 indicators:** How many Tier 2 criteria does client meet?
   - Sum up points from matched criteria
4. **Calculate confidence score (0-100):**
   - All hard requirements met + high Tier 1/2 points = 80-100 (High Confidence)
   - All hard requirements met + some points = 60-79 (Medium Confidence)
   - Hard requirements met + low points = 40-59 (Low Confidence)
   - Any hard requirement failed = 0-39 (Not Eligible)

### Step 4: Ranking
Clients sorted by confidence score (high to low).

### Step 5: PDF Generation
Ranked list formatted as branded PDF with:
- Company name, contact info, Account Executive
- Match rationale ("Why they qualify")
- Missing fields that need verification

### Step 6: Delivery
PDF emailed to Elias Tacher.

**Your criteria structure directly determines matching accuracy!**

---

## Testing & Validation

### Before You Deliver:

1. **Validate JSON structure:**
   ```bash
   python -m json.tool sdrp_criteria.json
   ```
   Should not have any syntax errors.

2. **Check all CRM fields exist:**
   Review `docs/ZOHO_CRM_DATA_ANALYSIS.md` and confirm every `crm_field` you specified is in Zoho.

3. **Verify completeness:**
   - All hard requirements from SDRP PDF captured?
   - All special provisions (specialty crops, AGI exceptions, etc.) included?
   - Disaster event list comprehensive?

4. **Test with sample client:**
   Manually apply your criteria to 1-2 sample client profiles from Zoho to see if logic makes sense.

### Deliverable Checklist:

- [ ] JSON file named: `sdrp_criteria.json`
- [ ] Valid JSON (no syntax errors)
- [ ] All hard requirements extracted
- [ ] All Tier 1 indicators extracted with point values
- [ ] All Tier 2 indicators extracted with point values
- [ ] All Tier 3 requirements extracted
- [ ] CRM field names match Zoho exactly
- [ ] Missing data actions specified for fields that don't exist
- [ ] Disaster event list is comprehensive

---

## Questions or Issues?

**Coordinating with:**
- **Bhuvana Raghu** (Zoho CRM integration owner) - if you need clarification on available fields or data quality
- **Matching Engine Team** - if you need the output format adjusted or have questions about downstream use

**Key Documents to Reference:**
1. `docs/ZOHO_CRM_DATA_ANALYSIS.md` - Full field inventory and data quality assessment
2. `docs/MATCHING_ENGINE_DESIGN.md` - Complete matching engine architecture (optional, for context)
3. SDRP eligibility criteria document (your input PDF)
4. SDRP Eligibility Criteria Framework (the detailed tier breakdown provided earlier)

---

## Example: Sample Criterion Extraction

**From SDRP PDF:** "Producer must be a U.S. citizen, resident alien, or entity wholly owned by eligible individuals."

**Your Output:**
```json
{
  "name": "citizenship",
  "description": "U.S. citizen, resident alien, or entity wholly owned by eligible individuals",
  "crm_field": "Citizenship_Status",
  "expected_values": ["US Citizen", "Resident Alien", "Eligible Entity"],
  "weight": "critical",
  "missing_data_action": "flag_for_manual_review"
}
```

**Reasoning:**
- This is a hard requirement (absolute disqualifier if not met)
- Field `Citizenship_Status` doesn't exist in Zoho CRM (per Phase 1 analysis)
- Can't exclude clients just because CRM is missing this data
- Action: Flag for manual review so AE can verify before application

---

**From SDRP PDF:** "Producers who received a crop insurance indemnity or NAP payment for 2023 or 2024 losses are eligible for Stage 1 with pre-filled application."

**Your Output:**
```json
{
  "name": "stage_1_insurance_indemnity",
  "description": "Received crop insurance indemnity or NAP payment for 2023/2024 losses",
  "crm_field": "Insurance_or_NAP_Coverage_2023_2024",
  "expected_values": ["Yes", "Received", "Indemnity Paid", "NAP Payment"],
  "weight": "high",
  "points": 10
}
```

**Reasoning:**
- This is Tier 1 (strongest qualification signal - pre-filled application!)
- Field exists in Zoho: `Insurance_or_NAP_Coverage_2023_2024` (52.6% filled)
- Highest point value (10) because Stage 1 is easiest path to payment
- Multiple expected values to catch variations in how data is entered

---

**Ready to build? Let me know if you need clarification on output format, field mapping, or tier classification!**

---

**Document Version:** 1.0
**Date:** May 12, 2026
**Owner:** Amanda Ford (Program Criteria Extraction)
**Coordinator:** Bhuvana Raghu (Zoho CRM Integration)
**Handoff To:** Matching Engine Team (TBD)
