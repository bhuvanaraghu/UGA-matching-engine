# Zoho CRM Data Quality Analysis
## United Grants of America - SDRP Matching Engine

**Prepared by:** Prism Digital Labs
**Date:** May 12, 2026
**Analysis Scope:** Accounts, Contacts, Farms modules
**Total Records Analyzed:** 2,053 records across 3 modules

---

## Executive Summary

This analysis evaluates the feasibility of building an SDRP (Supplemental Disaster Relief Program) matching engine using existing Zoho CRM data. Key findings:

### Overall Assessment: ✅ **FEASIBLE with Limitations**

- **Matchable Universe:** 213 farms (23% of total accounts) have sufficient SDRP-specific data
- **Data Quality Score:** 43% average across critical fields
- **High-Confidence Matches Possible:** ~120-150 farms (estimated 56-70% of 213)
- **Data Enrichment Required:** Critical fields missing for citizenship, ownership, and compliance verification

### Key Strengths
- ✅ Disaster event and loss data captured (58.7% coverage)
- ✅ Insurance and payment history tracked (52-59% coverage)
- ✅ Location data available (61-100% coverage)
- ✅ Contact information strong (85-91% for email/phone)

### Critical Gaps
- ❌ No citizenship/residency verification data
- ❌ No ownership share percentage tracking
- ❌ No conservation compliance (AD-1026) status
- ❌ No duplicate benefit checks (ERP 2022/ELAP)
- ❌ Missing exact insurance coverage percentages

---

## Data Inventory by Module

### Module 1: Accounts
**Total Records:** 921
**Overall Data Quality:** 33.6%
**Primary Purpose:** Client identification and basic information

#### High-Quality Fields (80%+ Fill Rate)
| Field Name | Fill Rate | Notes |
|------------|-----------|-------|
| Account_Name | 100.0% | Primary identifier - complete |
| Owner | 100.0% | Account owner assigned |
| Phone | 83.3% | Primary contact number |

#### Moderate-Quality Fields (50-79% Fill Rate)
| Field Name | Fill Rate | Notes |
|------------|-----------|-------|
| Type_of_Farm_Producer | 65.1% | Farm classification data |
| Have_tax_documents | 53.5% | Tax documentation status |
| Limited_Resource_Entity_Status | 53.5% | Entity classification |

#### Low-Quality Fields (<50% Fill Rate)
| Field Name | Fill Rate | Gap Impact |
|------------|-----------|------------|
| Account_Executive_Name | 35.5% | Difficult to route matches to AEs |
| FSA_County | 26.4% | Location matching limited |
| Lead_Source | 25.2% | Attribution tracking incomplete |
| NEW_State | 11.8% | Geographic matching constrained |
| Email | 0.0% | **CRITICAL** - No direct email in Accounts |

#### SDRP Relevance
**Limited Direct Use:** Accounts module lacks disaster-specific data. Primary value is client identification and linking to Contacts/Farms modules.

**Recommendation:** Use as join key only; pull actual matching criteria from Farms module.

---

### Module 2: Contacts
**Total Records:** 919 (nearly 1:1 with Accounts)
**Overall Data Quality:** 41.6%
**Primary Purpose:** Contact details and communication

#### High-Quality Fields (80%+ Fill Rate)
| Field Name | Fill Rate | Notes |
|------------|-----------|-------|
| Full_Name | 100.0% | Complete name data |
| Last_Name | 100.0% | Complete |
| First_Name | 90.5% | Nearly complete |
| Phone | 91.4% | **Excellent** for outreach |
| Account_Name | 87.7% | Strong linkage to Accounts |
| Email | 85.5% | **Excellent** for outreach |

#### Moderate-Quality Fields (50-79% Fill Rate)
| Field Name | Fill Rate | Notes |
|------------|-----------|-------|
| Mailing_State | 65.3% | Geographic data present |

#### Low-Quality Fields (<50% Fill Rate)
| Field Name | Fill Rate | Gap Impact |
|------------|-----------|------------|
| Account_Executive_Name | 35.1% | AE assignment incomplete |
| Mailing_City | 33.0% | Limits precise location matching |
| Mailing_Zip | 31.8% | Limits precise location matching |
| Mailing_Street | 31.6% | Full address rarely available |
| County | 30.6% | **CRITICAL for SDRP** - county-level disaster matching limited |

#### SDRP Relevance
**High Value for Outreach:** Strong email (85.5%) and phone (91.4%) coverage enables effective client communication. Moderate location data (65% state, 31% county) supports basic geographic matching.

**Recommendation:** Primary source for contact information in output PDFs. Supplement county data with Farms module (61% coverage there).

---

### Module 3: Farms
**Total Records:** 213 (only 23% of Accounts have Farm records!)
**Overall Data Quality:** 54.2%
**Primary Purpose:** **SDRP eligibility criteria and disaster loss data**

#### ⭐ This is Your Core SDRP Matching Module

#### Excellent Fields (80%+ Fill Rate)
| Field Name | Fill Rate | SDRP Tier | Notes |
|------------|-----------|-----------|-------|
| Farm_State | 100.0% | Hard Req. | Perfect state coverage |
| Farm_Executive | 100.0% | Output | Account Executive assignment |
| Account_TEST | 99.1% | - | Links to Accounts module |

#### Good Fields (50-79% Fill Rate)
| Field Name | Fill Rate | SDRP Tier | SDRP Criteria Mapped |
|------------|-----------|-----------|----------------------|
| **County** | 61.0% | Hard Req. + Tier 2 | Location for block grant exclusion + drought D2/D3 check |
| **What_They_Produce** | 59.6% | Tier 1 | Crop/commodity identification |
| **Livestock** | 59.6% | Tier 1 | Production type classification |
| **Preventing_Planting** | 59.2% | Tier 2 | Loss type indicator |
| **CT_HI_ME_MA_Losses** | 58.7% | Hard Req. | **Block grant state exclusion check** |
| **FSA_Forms_Up_to_Date** | 58.7% | Tier 3 | Compliance status |
| **Loss_Cause_2023_2024** | 58.7% | Hard Req. + Tier 1 | **Named disaster event type** |
| **Loss_Payments_Year_s** | 58.7% | Tier 1 | Payment history tracking |
| **Type_of_Crop_Insurance_2024_2023** | 58.7% | Tier 2 | Insurance type (not coverage %) |
| **Average_Annual_Revenue_from_crop_sales** | 58.2% | Tier 2 | Revenue context |
| **Control_County_Experience** | 58.2% | - | Experience level |
| **Analyst** | 55.9% | - | Internal assignment |
| **Insurance_or_NAP_Coverage_2023_2024** | 52.6% | Tier 1 | **Stage 1 eligibility indicator** |

#### Moderate Fields (30-49% Fill Rate)
| Field Name | Fill Rate | SDRP Tier | SDRP Criteria Mapped |
|------------|-----------|-----------|----------------------|
| **Losses_Crops_Trees_Vines_2023_2024** | 48.4% | Tier 2 | Tree/bush/vine loss indicator |
| **Additional_Information** | 45.1% | - | Supplementary notes |
| **Payment_Source_Losses** | 39.9% | Tier 1 | Where payments originated |
| **Entity_Members** | 34.7% | Hard Req. | Ownership structure (limited data) |
| **AGI_900K_75_Farm_Income** | 31.5% | Tier 2 | **≥75% AGI from farming** |
| **Farm_City** | 30.5% | Hard Req. | City-level location |

#### Low-Quality Fields (<30% Fill Rate)
| Field Name | Fill Rate | SDRP Tier | Gap Impact |
|------------|-----------|-----------|------------|
| Registered_Worked_with_FSA | 20.7% | Tier 1 | FSA relationship unknown for 79% |
| Acreage_Reporting | 20.2% | Tier 3 | Production verification limited |
| Insurance_Notes | 12.7% | Tier 2 | Coverage details sparse |
| Production_Quality_Loss_Status | 11.7% | Tier 2 | Stage 2 eligibility limited |
| Weather_Impact_Notes | 10.8% | Tier 1 | Disaster context missing |
| Losses_From_Previous_Year_Weather | 9.4% | Hard Req. | Multi-year loss tracking poor |

#### SDRP Relevance
**Primary Matching Source:** This module contains the majority of SDRP-specific eligibility fields. 58.7% coverage on critical fields (disaster event, insurance, loss payments, block grant exclusion) enables meaningful matching for ~125 farms.

**Critical Limitation:** Only 213 of 921 accounts (23%) have Farm records. This defines the maximum matchable universe.

**Recommendation:** Build matching engine around Farms module. Join to Accounts/Contacts for complete profile. Flag records with <50% field completeness as "Low Confidence."

---

## SDRP Criteria Mapping Analysis

### Hard Requirements Coverage

| SDRP Requirement | Zoho Field Available? | Module | Fill Rate | Gap Assessment |
|------------------|----------------------|--------|-----------|----------------|
| **Citizenship/Residency Status** | ❌ NO | - | 0% | **CRITICAL GAP** - Must collect or assume eligible |
| **Ownership Share & Risk** | ⚠️ Partial | Farms.Entity_Members | 34.7% | **HIGH GAP** - Share % not structured |
| **State & County Location** | ✅ YES | Farms.Farm_State, Farms.County | 100% / 61% | **GOOD** - State perfect, county good |
| **Disaster Event Type** | ✅ YES | Farms.Loss_Cause_2023_2024 | 58.7% | **MODERATE** - 41% missing event data |
| **Disaster Year 2023/2024** | ⚠️ Inferred | Farms.Loss_Payments_Year_s | 58.7% | **MODERATE** - Year may need parsing |
| **Conservation Compliance (AD-1026)** | ❌ NO | - | 0% | **CRITICAL GAP** - No tracking field |
| **No Duplicate Benefits (ERP 2022)** | ❌ NO | - | 0% | **CRITICAL GAP** - External check required |
| **No Duplicate Benefits (ELAP)** | ❌ NO | - | 0% | **CRITICAL GAP** - External check required |
| **Block Grant State Exclusion** | ✅ YES | Farms.CT_HI_ME_MA_Losses | 58.7% | **GOOD** - Directly tracked |
| **Future Insurance Linkage Agreement** | ⚠️ Inferred | Farms.Insurance_or_NAP_Coverage | 52.6% | **MODERATE** - Current status, not future commitment |

### Tier 1 Strong Indicators Coverage

| SDRP Indicator | Zoho Field Available? | Module | Fill Rate | Match Strength |
|----------------|----------------------|--------|-----------|----------------|
| **Stage 1: Insurance Indemnity/NAP Payment** | ✅ YES | Farms.Insurance_or_NAP_Coverage_2023_2024 | 52.6% | **HIGH** - Direct Stage 1 signal |
| **Named Qualifying Disaster Event** | ✅ YES | Farms.Loss_Cause_2023_2024 | 58.7% | **HIGH** - Event type tracked |
| **Ownership Share & At-Risk Status** | ⚠️ Partial | Farms.Entity_Members | 34.7% | **LOW** - Unstructured data |
| **Specialty/High-Value Crop** | ⚠️ Indirect | Accounts.Farm_Grows_Produces_Specialty_crops, Farms.What_They_Produce | 100% / 59.6% | **MODERATE** - Boolean flag + text field, needs interpretation |

### Tier 2 Moderate Indicators Coverage

| SDRP Indicator | Zoho Field Available? | Module | Fill Rate | Usability |
|----------------|----------------------|--------|-----------|-----------|
| **Crop Insurance Coverage Level (%)** | ⚠️ Type Only | Farms.Type_of_Crop_Insurance_2024_2023 | 58.7% | **PARTIAL** - Have type, not exact % for SDRP Factor calculation |
| **AGI ≥75% from Farming** | ✅ YES | Farms.AGI_900K_75_Farm_Income | 31.5% | **MODERATE** - Lower coverage limits high-cap matches |
| **Stage 2: Shallow Loss Eligibility** | ⚠️ Partial | Farms.Production_Quality_Loss_Status | 11.7% | **LOW** - Very limited Stage 2 data |
| **Tree/Bush/Vine Losses** | ✅ YES | Farms.Losses_Crops_Trees_Vines_2023_2024 | 48.4% | **MODERATE** - Decent coverage for specialty payments |
| **High-Disaster-Impact County** | ✅ YES | Farms.County | 61.0% | **GOOD** - Can cross-reference with U.S. Drought Monitor |

### Tier 3 Supporting Details Coverage

| SDRP Requirement | Zoho Field Available? | Module | Fill Rate | Administrative Impact |
|------------------|----------------------|--------|-----------|----------------------|
| **Conservation Compliance (AD-1026)** | ❌ NO | - | 0% | **HIGH** - Payment blocker if not on file |
| **Verifiable Production Records** | ⚠️ Status Only | Farms.Production_Quality_Loss_Status | 11.7% | **MODERATE** - Availability tracked poorly |
| **Farm Operating Plan (CCC-902/901)** | ⚠️ Indirect | Farms.FSA_Forms_Up_to_Date | 58.7% | **MODERATE** - General status, not specific form |
| **Quality Loss Documentation** | ⚠️ Status Only | Farms.Production_Quality_Loss_Status | 11.7% | **LOW** - Limited tracking |
| **Linkage Agreement Confirmation** | ⚠️ Current Only | Farms.Insurance_or_NAP_Coverage | 52.6% | **MODERATE** - Future agreement not tracked |

---

## Data Quality Scoring by Confidence Level

### High-Confidence Matches (Estimated: 120-150 farms)
**Criteria:** Farm record exists + ≥50% of critical SDRP fields populated

**Available Fields:**
- Disaster event type and year
- Insurance/NAP coverage status
- Loss payment history
- Location (state + county)
- Block grant state check
- Crop/commodity information

**Missing Fields (Manual Review Required):**
- Citizenship verification
- Ownership share percentage
- AD-1026 compliance status
- Exact insurance coverage %
- ERP 2022/ELAP duplicate check

**Recommendation:** Process for matching with "High Confidence" flag. Require manual review of missing fields before final approval.

---

### Medium-Confidence Matches (Estimated: 50-80 farms)
**Criteria:** Farm record exists + 30-49% of critical SDRP fields populated

**Likely Issues:**
- Missing disaster event details
- Unknown insurance status
- Limited location data (state only, no county)
- AGI from farming unknown

**Recommendation:** Include in output with "Medium Confidence - Additional Information Needed" flag. Prioritize for data enrichment follow-up.

---

### Low-Confidence / Exclude (Estimated: 708 accounts without Farms)
**Criteria:** No Farm record OR <30% critical fields populated

**Data Available:**
- Account name
- Contact information (email/phone)
- Specialty crop flag (boolean only)

**Recommendation:** Exclude from SDRP matching. These accounts lack sufficient disaster loss and eligibility data. Consider for future program matching after data enrichment.

---

## Critical Data Gaps & Remediation

### Gap Category 1: Hard Requirement Blockers
**Impact:** Cannot verify absolute eligibility without this data

| Missing Field | SDRP Requirement | Workaround | Effort Level |
|---------------|------------------|------------|--------------|
| **Citizenship/Residency Status** | U.S. citizen or resident alien | Assume eligible for initial match; verify during application | Medium |
| **Ownership Share %** | Must have share at risk | Extract from Entity_Members text field (34.7% have data); Request for others | High |
| **AD-1026 Compliance** | Conservation compliance required | Add boolean field to Farms; Backfill via FSA records or client survey | High |
| **ERP 2022 Payment History** | No duplicate benefits | Cross-reference with external FSA payment database | Medium |
| **ELAP Payment History** | No duplicate benefits (aquaculture) | Cross-reference with external FSA payment database | Low (affects few clients) |

**Recommended Actions:**
1. **Immediate:** Add `Citizenship_Status` (dropdown: US Citizen / Resident Alien / Other) and `AD_1026_On_File` (boolean) fields to Farms module
2. **Short-term:** Extract ownership percentages from `Entity_Members` text field using NLP/Claude parsing
3. **Integration:** Connect to FSA payment database for ERP 2022/ELAP duplicate checks (if API available)

---

### Gap Category 2: Payment Calculation Limitations
**Impact:** Cannot calculate precise SDRP payment amounts; can only rank eligibility

| Missing Field | SDRP Usage | Current Data | Enhancement Needed |
|---------------|------------|--------------|-------------------|
| **Exact Coverage % (60/100, 65/100, 80/100, etc.)** | SDRP Factor (75%-95%) | Insurance type only | Add `Coverage_Level_Percentage` field; Integrate with RMA records |
| **Producer Certified Share %** | Payment multiplier | Unstructured in Entity_Members | Structure as numeric field `Producer_Share_Percent` |
| **County Disaster Yield (CDY)** | Stage 2 payment calculation | Not tracked | Add field or integrate with USDA county yield database |
| **Unharvested Crop Flag** | Payment adjustment | Not tracked | Add boolean `Crop_Harvested` field |

**Recommended Actions:**
1. **High Priority:** Add `Coverage_Level_Percentage` field to capture exact insurance coverage (required for SDRP Factor)
2. **High Priority:** Structure `Producer_Share_Percent` as numeric field (0-100%)
3. **Medium Priority:** Add `Crop_Harvested` boolean for unharvested adjustments
4. **Low Priority:** CDY can be pulled from external USDA database by county

---

### Gap Category 3: Match Quality Improvements
**Impact:** Enhances ranking accuracy and reduces false positives

| Enhancement Area | Current State | Recommended Addition | Benefit |
|------------------|---------------|---------------------|---------|
| **Stage 2 Eligibility Tracking** | Production_Quality_Loss_Status (11.7%) | Add structured fields: `Loss_Below_Deductible` (boolean), `Shallow_Loss_Amount` | Identify Stage 2 candidates accurately |
| **Quality Loss Details** | Production_Quality_Loss_Status (11.7%) | Add: `Quality_Loss_Percentage`, `Grading_Test_Date`, `Nutrient_Test_Results` | Support quality adjustment claims |
| **Multi-Year Loss Tracking** | Losses_From_Previous_Year_Weather (9.4%) | Expand to: `Loss_Year_2023`, `Loss_Year_2024`, `Loss_Year_2022` (separate booleans) | Prevent confusion between disaster years |
| **Insurance Notes Standardization** | Insurance_Notes (12.7% free text) | Add structured: `Policy_Number`, `Insurance_Company`, `Adjuster_Contact` | Improve Stage 1 verification |
| **FSA Relationship Detail** | Registered_Worked_with_FSA (20.7%) | Add: `FSA_County_Office` (lookup), `FSA_Farm_Number`, `Customer_Core_ID_CCID` | Enable pre-filled application check |

**Recommended Actions:**
1. **Quick Win:** Improve `Insurance_Notes` fill rate from 12.7% to 50%+ through AE outreach campaign
2. **Data Structure:** Replace free-text `Production_Quality_Loss_Status` with structured loss tracking fields
3. **FSA Integration:** Add Customer Core ID (CCID) field to enable RMA/FSA record linkage

---

### Gap Category 4: Operational Efficiency
**Impact:** Reduces manual work and improves output quality

| Efficiency Gap | Current Challenge | Recommendation |
|----------------|-------------------|----------------|
| **Account Executive Assignment** | Only 35.5% of accounts have AE assigned | Backfill missing assignments; Make field mandatory for new records |
| **County-Level Location** | 61% in Farms, 30.6% in Contacts, 26.4% in Accounts | Standardize on Farms.County (best coverage); Backfill from other modules |
| **Email Routing** | 0% in Accounts, 85.5% in Contacts | Always join to Contacts for email; Consider adding to Farms for direct access |
| **Specialty Crop Identification** | Boolean in Accounts + text in Farms | Create standard dropdown: Fruits, Tree Nuts, Vegetables, Herbs, Orchards, Vineyards, Other, Non-Specialty |

**Recommended Actions:**
1. **Process Improvement:** Require AE assignment at account creation
2. **Data Normalization:** Consolidate county data to Farms module as single source of truth
3. **UX Enhancement:** Add Farms.Contact_Email to avoid multi-table joins in matching engine

---

## Recommendations by Priority

### Immediate (Before Building Matching Engine)

1. **Add Critical Missing Fields to Farms Module:**
   - `Citizenship_Status` (dropdown: US Citizen | Resident Alien | Other)
   - `AD_1026_On_File` (boolean)
   - `Coverage_Level_Percentage` (number: 50-85)
   - `Producer_Share_Percent` (number: 0-100)
   - `Contact_Email` (text - copy from Contacts)

2. **Data Enrichment Campaign:**
   - Backfill Account Executive assignments (target 80%+)
   - Improve Insurance_Notes coverage (target 50%+)
   - Capture missing county data (target 75%+)

3. **Create Data Join Strategy:**
   - Document: Accounts → Contacts → Farms relationship
   - Define: Primary source for each SDRP field
   - Build: Matching engine pulls from all 3 modules

**Estimated Effort:** 2-3 weeks (1 week field additions + 1-2 weeks backfill campaign)

---

### Short-Term (Post-MVP)

1. **Structure Unstructured Fields:**
   - Parse `Entity_Members` text to extract ownership percentages
   - Standardize `What_They_Produce` into commodity classification
   - Replace `Production_Quality_Loss_Status` free text with structured loss fields

2. **External Data Integration:**
   - FSA payment database (ERP 2022/ELAP duplicate check)
   - U.S. Drought Monitor API (D2/D3 county ratings)
   - RMA insurance records (exact coverage levels, indemnity history)

3. **Validation Rules:**
   - Require county if state = (not CT/HI/ME/MA)
   - Require insurance coverage % if insurance type is populated
   - Require disaster event if loss payments year = 2023 or 2024

**Estimated Effort:** 4-6 weeks

---

### Long-Term (Scalability & Automation)

1. **RingSense Integration:**
   - Extract disaster details from call transcripts
   - Auto-populate insurance status from AE conversations
   - Flag AGI/income mentions for follow-up

2. **Automated Data Quality Monitoring:**
   - Weekly completeness reports by Account Executive
   - Alert when critical fields missing on new Farm records
   - Dashboard showing match-ready vs. data-incomplete farms

3. **Multi-Program Support:**
   - Generalize eligibility tracking beyond SDRP
   - Create reusable criteria framework
   - Build program-to-client recommendation engine

**Estimated Effort:** 8-12 weeks

---

## Module Relationship & Data Flow

### Current Data Model

```
Accounts (921 records)
    ↓ [Linked by Account_Name]
Contacts (919 records) ← Email, Phone, Location
    ↓ [Linked by Account]
Farms (213 records) ← SDRP Eligibility Criteria

Only 213 of 921 accounts have Farms records!
```

### Recommended Join Strategy for Matching Engine

```sql
SELECT
    a.Account_Name,
    c.Email,
    c.Phone,
    c.Mailing_State,
    c.County AS Contact_County,
    f.Farm_State,
    f.County AS Farm_County,
    f.Loss_Cause_2023_2024,
    f.Insurance_or_NAP_Coverage_2023_2024,
    f.Type_of_Crop_Insurance_2024_2023,
    f.Loss_Payments_Year_s,
    f.CT_HI_ME_MA_Losses,
    f.AGI_900K_75_Farm_Income,
    f.What_They_Produce,
    f.Losses_Crops_Trees_Vines_2023_2024,
    f.Farm_Executive AS Account_Executive
FROM
    Farms f
    INNER JOIN Accounts a ON f.Account_TEST = a.id
    LEFT JOIN Contacts c ON c.Account_Name = a.Account_Name
WHERE
    f.Farm_State IS NOT NULL
    AND f.Farm_State NOT IN ('CT', 'HI', 'ME', 'MA') -- Block grant exclusion
ORDER BY
    /* Confidence score calculation */
    (CASE WHEN f.Loss_Cause_2023_2024 IS NOT NULL THEN 1 ELSE 0 END) +
    (CASE WHEN f.Insurance_or_NAP_Coverage_2023_2024 IS NOT NULL THEN 1 ELSE 0 END) +
    (CASE WHEN f.Loss_Payments_Year_s IS NOT NULL THEN 1 ELSE 0 END) +
    (CASE WHEN f.County IS NOT NULL THEN 1 ELSE 0 END) DESC
```

**Key Logic:**
- Start with Farms (only matchable records)
- Join to Accounts for identification
- Join to Contacts for communication
- Exclude block grant states immediately
- Rank by number of critical fields populated

---

## Conclusion & Go/No-Go Decision

### ✅ GO Decision: Build SDRP Matching Engine

**Justification:**
- 213 farms have sufficient data for eligibility assessment
- 58.7% coverage on critical disaster/insurance fields enables meaningful matching
- ~120-150 high-confidence matches achievable (56-70% of matchable universe)
- Contact information (email/phone) strong for outreach (85-91%)

**Conditions:**
1. Accept that only 23% of accounts are currently matchable (213 of 921)
2. Implement confidence scoring (High/Medium/Low) based on field completeness
3. Require manual review for missing hard requirements (citizenship, AD-1026, ownership %)
4. Add 5 critical fields to Farms module before launch (see Immediate Recommendations)
5. Plan Phase 2 data enrichment to expand matchable universe to 500+ farms

**Expected Outcomes (Phase 1):**
- **High Confidence Matches:** 120-150 farms ready for SDRP application (manual review of 3-5 fields required)
- **Medium Confidence Matches:** 50-80 farms with partial data (require client follow-up for missing info)
- **Low Confidence / Exclude:** 708 accounts without Farm records (defer to future programs)

**Timeline to Launch:**
- Immediate field additions: 1 week
- Data enrichment campaign: 1-2 weeks
- Matching engine build: 2-3 weeks (parallel with enrichment)
- **Total:** 4-6 weeks to first match run

---

## Appendix A: Field Inventory by Module

### Accounts Module - Complete Field List (921 records)

| Field Name | Fill Rate | Data Type | SDRP Relevance |
|------------|-----------|-----------|----------------|
| Account_Name | 100.0% | Text | Primary identifier |
| Owner | 100.0% | Lookup | Internal routing |
| Account_With_FSA | 100.0% | Boolean | FSA relationship indicator |
| Farm_Grows_Produces_Specialty_crops | 100.0% | Boolean | Tier 1 indicator (basic) |
| Farm_Operation_Over_10_Years | 100.0% | Boolean | Experience indicator |
| Phone | 83.3% | Phone | Contact info |
| Type_of_Farm_Producer | 65.1% | Dropdown | Farm classification |
| Have_tax_documents | 53.5% | Boolean | Documentation status |
| Limited_Resource_Entity_Status | 53.5% | Boolean | Entity classification |
| Account_Executive_Name | 35.5% | Text | Output field - who to contact |
| FSA_County | 26.4% | Text | Location (limited coverage) |
| Lead_Source | 25.2% | Dropdown | Attribution |
| NEW_State | 11.8% | Text | Location (very limited) |
| *All location fields (Billing/Mailing)* | 0.0% | Text | Fields not in use |

### Contacts Module - Complete Field List (919 records)

| Field Name | Fill Rate | Data Type | SDRP Relevance |
|------------|-----------|-----------|----------------|
| Full_Name | 100.0% | Text | Contact identification |
| Last_Name | 100.0% | Text | Contact identification |
| Owner | 100.0% | Lookup | Internal routing |
| First_Name | 90.5% | Text | Contact identification |
| Phone | 91.4% | Phone | **Primary outreach method** |
| Account_Name | 87.7% | Lookup | Links to Accounts |
| Email | 85.5% | Email | **Primary outreach method** |
| Mailing_State | 65.3% | Text | Location data |
| Account_Executive_Name | 35.1% | Text | AE assignment |
| Mailing_City | 33.0% | Text | Location data |
| Mailing_Zip | 31.8% | Text | Location data |
| Mailing_Street | 31.6% | Text | Full address (rare) |
| County | 30.6% | Text | **SDRP county matching** |

### Farms Module - Complete Field List (213 records)

**⭐ Primary SDRP Matching Source**

| Field Name | Fill Rate | SDRP Tier | Description |
|------------|-----------|-----------|-------------|
| **Identity & Linkage** ||||
| Name | 100.0% | - | Farm identifier |
| Client_First_Name | 100.0% | - | Client link |
| Client_Last_Name | 100.0% | - | Client link |
| Farm_Executive | 100.0% | Output | Account Executive |
| Account_TEST | 99.1% | - | Links to Accounts |
| **Location** ||||
| Farm_State | 100.0% | Hard Req. | State location |
| County | 61.0% | Hard Req. + Tier 2 | County for disaster matching |
| Farm_City | 30.5% | Hard Req. | City location |
| **Disaster & Loss Data** ||||
| Loss_Cause_2023_2024 | 58.7% | Hard Req. + Tier 1 | Named disaster event |
| Loss_Payments_Year_s | 58.7% | Tier 1 | Payment year(s) |
| Losses_Crops_Trees_Vines_2023_2024 | 48.4% | Tier 2 | Tree/vine loss indicator |
| CT_HI_ME_MA_Losses | 58.7% | Hard Req. | Block grant exclusion |
| Losses_From_Previous_Year_Weather | 9.4% | Hard Req. | Multi-year tracking (poor) |
| Weather_Impact_Notes | 10.8% | Tier 1 | Disaster details (poor) |
| **Insurance & Payments** ||||
| Insurance_or_NAP_Coverage_2023_2024 | 52.6% | Tier 1 | **Stage 1 eligibility** |
| Type_of_Crop_Insurance_2024_2023 | 58.7% | Tier 2 | Insurance type |
| Payment_Source_Losses | 39.9% | Tier 1 | Payment origin |
| Insurance_Notes | 12.7% | Tier 2 | Coverage details (poor) |
| **Crop & Production** ||||
| What_They_Produce | 59.6% | Tier 1 | Crop/commodity |
| Livestock | 59.6% | Tier 1 | Production type |
| Preventing_Planting | 59.2% | Tier 2 | Loss type |
| Production_Quality_Loss_Status | 11.7% | Tier 2 | Stage 2 indicator (poor) |
| **Financial** ||||
| AGI_900K_75_Farm_Income | 31.5% | Tier 2 | ≥75% AGI from farming |
| Average_Annual_Revenue_from_crop_sales | 58.2% | Tier 2 | Revenue context |
| **Compliance & Admin** ||||
| FSA_Forms_Up_to_Date | 58.7% | Tier 3 | Forms compliance |
| Registered_Worked_with_FSA | 20.7% | Tier 1 | FSA relationship |
| Acreage_Reporting | 20.2% | Tier 3 | Production records |
| **Ownership & Entity** ||||
| Entity_Members | 34.7% | Hard Req. | Ownership structure (unstructured) |
| Control_County_Experience | 58.2% | - | Experience level |

---

## Appendix B: Confidence Scoring Formula

### Recommended Approach

**High Confidence Match (Score 8-12):**
```
Score =
  + 2 points if Loss_Cause_2023_2024 filled (disaster event)
  + 2 points if Insurance_or_NAP_Coverage_2023_2024 filled (Stage 1)
  + 2 points if Loss_Payments_Year_s filled (payment history)
  + 1 point if County filled (location matching)
  + 1 point if Type_of_Crop_Insurance filled (coverage type)
  + 1 point if What_They_Produce filled (commodity)
  + 1 point if AGI_900K_75_Farm_Income filled (payment cap)
  + 1 point if Losses_Crops_Trees_Vines filled (specialty payment)
  + 1 point if CT_HI_ME_MA_Losses = "No" (not block grant state)

Maximum Score: 12 points
High Confidence Threshold: 8+ points (≥67% of weighted criteria met)
```

**Medium Confidence Match (Score 5-7):**
- Has Farm record
- Some disaster/insurance data present
- Location data present
- Missing 3-5 critical fields

**Low Confidence / Exclude (Score 0-4):**
- No Farm record OR
- Missing disaster event data OR
- Missing location data OR
- Block grant state with no override

---

## Appendix C: Data Enrichment Priority Matrix

| Field to Add/Improve | Current State | Target State | Impact on Matches | Effort | Priority |
|----------------------|---------------|--------------|-------------------|--------|----------|
| Citizenship_Status | 0% (not tracked) | 80% captured | Removes #1 blocker | Medium | **Critical** |
| AD_1026_On_File | 0% (not tracked) | 80% captured | Removes #2 blocker | High | **Critical** |
| Coverage_Level_Percentage | Type only (58.7%) | 70% exact % | Enables SDRP Factor calculation | Medium | **Critical** |
| Producer_Share_Percent | Unstructured (34.7%) | 70% structured | Enables payment calculation | High | **High** |
| Account_Executive_Name | 35.5% in Accounts | 90% complete | Improves output routing | Low | **High** |
| County | 61% in Farms | 85% complete | Improves location matching | Medium | **High** |
| Insurance_Notes | 12.7% filled | 60% filled | Improves Stage 1 verification | Medium | Medium |
| Production_Quality_Loss_Status | 11.7% filled | 40% structured | Enables Stage 2 matching | High | Medium |
| Customer_Core_ID_CCID | 0% (not tracked) | 50% captured | Enables pre-fill check | Medium | Medium |
| Ownership_Share_Details | 34.7% unstructured | 70% structured | Supports at-risk verification | High | Medium |

---

**Document Version:** 1.0
**Analysis Date:** May 12, 2026
**Records Analyzed:** 2,053 (Accounts: 921, Contacts: 919, Farms: 213)
**Prepared By:** Prism Digital Labs - Zoho CRM Integration Team
**Contact:** bhuvana@prismdigitallabs.com

---

**END OF REPORT**
