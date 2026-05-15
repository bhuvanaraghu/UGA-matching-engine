# UGA Matching Engine - Complete Specification
**Project:** United Grants of America - Engagement 4
**Date:** May 15, 2026
**Status:** Design Phase - Ready for Implementation

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Amanda's Deliverable](#amandas-deliverable)
3. [System Architecture](#system-architecture)
4. [Implementation Plan](#implementation-plan)
5. [Cost & Timeline](#cost--timeline)

---

## Executive Summary

### What We're Building
An automated system that matches UGA's 213 farm clients against USDA grant programs (starting with SDRP), producing a ranked PDF of eligible matches delivered to Elias Tacher.

### How It Works
```
Program PDF → Claude extracts criteria → Match 213 clients → Rank by confidence → PDF report → Email
```

### Key Details
- **Architecture:** Serverless (runs on-demand, no hosting)
- **AI Model:** Claude Sonnet 4.6 with prompt caching
- **Data Source:** Zoho CRM (Accounts, Contacts, Farms)
- **Cost:** $5-10 per run
- **Build Time:** 23 hours
- **Add New Program:** 30 minutes

### Current Status
✅ **Phase 1 Complete:** Zoho CRM integration built, 213 matchable farms identified
🔄 **Phase 2 In Progress:** Amanda converting SDRP criteria to JSON (2-3 hours)
⏳ **Phase 2 Pending:** Matching engine build (23 hours)

---

## Amanda's Deliverable

### What You Need to Deliver
**File:** `sdrp_criteria.json`

Convert your existing SDRP criteria markdown into this JSON structure:

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
    }
  ],

  "tier_1_indicators": [
    {
      "name": "stage_1_insurance_indemnity",
      "description": "Received insurance indemnity or NAP payment",
      "crm_field": "Insurance_or_NAP_Coverage_2023_2024",
      "expected_values": ["Yes", "Received"],
      "weight": "high",
      "points": 10
    }
  ],

  "tier_2_indicators": [
    {
      "name": "agi_75_percent_farming",
      "description": "≥75% of AGI from farming",
      "crm_field": "AGI_900K_75_Farm_Income",
      "expected_values": [true, "Yes"],
      "weight": "medium",
      "points": 5
    }
  ],

  "tier_3_requirements": [
    {
      "name": "conservation_compliance",
      "description": "AD-1026 form on file",
      "crm_field": "AD_1026_On_File",
      "weight": "low",
      "required_for_payment": true
    }
  ]
}
```

### Field Mapping Reference

| Your Criteria | Zoho CRM Field | Fill Rate | Notes |
|--------------|----------------|-----------|-------|
| State/County | `Farm_State`, `County` | 100%, 61% | ✅ Good coverage |
| Disaster event | `Loss_Cause_2023_2024` | 58.7% | ✅ Tracked |
| Insurance/NAP | `Insurance_or_NAP_Coverage_2023_2024` | 52.6% | ✅ Available |
| Specialty crop | `Farm_Grows_Produces_Specialty_crops` | 100% | ✅ Perfect |
| Citizenship | ❌ **Does not exist** | 0% | Set `missing_data_action: "flag_for_manual_review"` |
| AD-1026 | ❌ **Does not exist** | 0% | Set `missing_data_action: "flag_for_manual_review"` |

**Full field list:** See `ZOHO_CRM_DATA_ANALYSIS.md` Appendix A

### Classification Guide

**Hard Requirements (Pass/Fail)**
- Absolute disqualifiers
- Example: Must be US citizen, not in CT/HI/ME/MA, disaster in 2023-2024

**Tier 1 Indicators (8-10 points)**
- Strong qualification signals
- Example: Received insurance indemnity, specialty crop, named disaster event

**Tier 2 Indicators (3-6 points)**
- Moderate signals, tie-breakers
- Example: AGI ≥75% from farming, crop insurance coverage level

**Tier 3 Requirements (No points)**
- Administrative/documentation needs
- Example: AD-1026 form, production records, application forms

### Validation Before Delivery
```bash
# Test JSON syntax
python -m json.tool sdrp_criteria.json

# Checklist
□ All hard requirements extracted
□ Tier 1/2 indicators with point values
□ Tier 3 requirements listed
□ CRM field names match Zoho exactly (case-sensitive!)
□ Missing data actions specified
```

---

## System Architecture

### Workflow
```
Step 1: Amanda delivers sdrp_criteria.json
           ↓
Step 2: Fetch 213 client profiles from Zoho (Accounts→Contacts→Farms)
           ↓
Step 3: For each client, Claude evaluates:
        - Hard requirements → Pass/Fail
        - Tier 1 indicators → Sum points
        - Tier 2 indicators → Sum points
        - Confidence score → 0-100
           ↓
Step 4: Sort by confidence, group into High/Medium/Low tiers
           ↓
Step 5: Generate branded PDF with ranked matches
           ↓
Step 6: Email PDF to Elias
```

### Sample Output
```json
{
  "company_name": "Smith Family Farms",
  "contact_name": "John Smith",
  "phone": "555-0100",
  "email": "john@smithfarms.com",
  "account_executive": "Allan Vargas",
  "confidence_score": 95,
  "tier": "High",
  "match_rationale": "Strong match: Received insurance indemnity for 2023 wildfire losses.
                      Farm grows specialty crops. All hard requirements met.",
  "missing_fields": ["Citizenship_Status", "AD_1026_On_File"],
  "recommended_action": "Contact immediately"
}
```

### Confidence Scoring
- **80-100 (High):** Meets all hard requirements + multiple Tier 1 indicators + good data completeness
- **60-79 (Medium):** Meets requirements but missing some data or weaker indicators
- **40-59 (Low):** Meets requirements but significant data gaps
- **0-39 (Not Eligible):** Failed hard requirements or insufficient data

### Cost Optimization: Prompt Caching
- Cache program criteria once (1,500 tokens)
- Reuse for all 213 client evaluations
- **Result:** 90% cost reduction ($2 vs. $8 per run)

---

## Implementation Plan

### Build Steps (23 hours)

| Step | Task | Hours | Owner | Status |
|------|------|-------|-------|--------|
| 1 | Program criteria extraction (JSON conversion) | 3 | Amanda | 🔄 In Progress |
| 2 | Client data assembly (Zoho → profiles) | 2 | Dev | ⏳ Pending |
| 3 | Matching logic (Claude evaluation per client) | 8 | Dev | ⏳ Pending |
| 4 | Ranking & filtering | 2 | Dev | ⏳ Pending |
| 5 | PDF generation (branded report) | 6 | Dev | ⏳ Pending |
| 6 | Email delivery | 2 | Dev | ⏳ Pending |

### Reusable Assets (Already Built ✅)
- `ZohoCRMClient` class - fetch from any module
- `DataQualityAnalyzer` class - field completeness analysis
- OAuth token refresh automation

### Testing Strategy
1. **Sample test (20 clients)** - validate matching logic accuracy
2. **Full run (213 clients)** - complete processing
3. **Manual review** - spot check top 20 matches before delivery

---

## Cost & Timeline

### One-Time Build Cost
| Item | Cost |
|------|------|
| Development (23 hours @ $150/hr) | $3,450 |

### Per-Run Cost (Recurring)
| Item | Cost |
|------|------|
| Claude API (213 clients, with caching) | $5-10 |
| Zoho CRM API | $0 (included) |
| Email delivery | $0 (Gmail SMTP) |
| **Total per run** | **$5-10** |

### ROI
- **Annual cost:** 4 programs × $10 = **$40/year**
- **Manual alternative:** 213 clients × 15 min = 53 hours = **$8,000**
- **Savings:** **$7,960 per run**
- **Payback:** First run

### Timeline
- Amanda's JSON delivery: 2-3 hours (🔄 this week)
- Development: 23 hours (⏳ 3 days)
- Testing & delivery: 1 day
- **Total:** ~1 week from Amanda's delivery

---

## Future Enhancements

### Phase 3: Document Search (Optional)
Extract data from Zoho CRM attachments (902 forms, intake docs) to fill missing fields.
**Effort:** 10-15 hours

### Phase 4: RingSense Integration (Optional)
Extract eligibility details from AE call transcripts to supplement CRM data.
**Effort:** 15-20 hours

### Phase 5: Scheduled Automation (Optional)
Deploy as AWS Lambda, runs monthly, delivers PDFs automatically.
**Effort:** 5-8 hours

### Phase 6: Multi-Program Matching (Optional)
Match clients to ALL programs at once, recommend best fit per client.
**Effort:** 8-12 hours

---

## Success Metrics

### Phase 2 Completion
- [ ] SDRP criteria extracted as JSON
- [ ] 213 client profiles assembled from Zoho
- [ ] Sample test ≥85% accuracy
- [ ] Full run completes without critical errors
- [ ] PDF delivered to Elias
- [ ] Elias confirms report is actionable

### Post-Delivery (30 days)
- [ ] AE team contacts top 20 matches
- [ ] ≥50% confirm eligibility
- [ ] ≥1 application submitted
- [ ] Elias approves for next program

---

## Questions?

**Amanda:** Need help with JSON format or field mapping? See `ZOHO_CRM_DATA_ANALYSIS.md` or sync with Bhuvana.

**Elias/UGA Team:** Questions about the design or want to add features? Let's discuss before building.

---

**END OF DOCUMENT**

**Version:** 2.0
**Pages:** 8 (much better than 100! 😅)
**Status:** Ready for implementation
