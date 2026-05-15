# UGA Matching Engine - Technical Design Document
## Program-Client Matching System Architecture

**Project:** United Grants of America - Engagement 4
**Document Version:** 1.0
**Date:** May 12, 2026
**Status:** Design Phase - No Code Written
**Prepared By:** Prism Digital Labs

---

## Executive Summary

This document outlines the technical architecture for building a program-client matching engine that automatically identifies which UGA clients are eligible for USDA grant programs. The system uses Claude AI to reason across complex eligibility criteria and matches them against 500+ client records in Zoho CRM, producing a ranked PDF of high-confidence matches delivered directly to the UGA leadership team.

**Key Design Decisions:**
- **Architecture**: Serverless, on-demand execution (no continuously running infrastructure)
- **AI Model**: Claude Sonnet 4.6 with prompt caching for cost efficiency
- **Data Source**: Zoho CRM API (Accounts, Contacts, Farms modules)
- **Output**: Branded PDF with ranked matches, delivered via email
- **Cost**: ~$5-10 per 500-client run
- **Scalability**: Program-agnostic design - add new programs without code changes

---

## System Architecture Overview

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     MATCHING ENGINE WORKFLOW                     │
└─────────────────────────────────────────────────────────────────┘

1. INPUT LAYER
   ┌──────────────────────┐      ┌──────────────────────┐
   │  Program PDF         │      │  Zoho CRM API        │
   │  (SDRP Criteria)     │      │  (500+ Clients)      │
   └──────────┬───────────┘      └──────────┬───────────┘
              │                              │
              └──────────────┬───────────────┘
                             ▼
2. EXTRACTION & PREPARATION
   ┌─────────────────────────────────────────┐
   │  Program Criteria Extraction            │
   │  • Parse PDF with Claude                │
   │  • Structure eligibility rules          │
   │  • Cache for reuse (90% cost savings)   │
   └──────────────────┬──────────────────────┘
                      │
                      ▼
   ┌─────────────────────────────────────────┐
   │  Client Data Assembly                   │
   │  • Fetch from Zoho (Accounts→Contacts→Farms) │
   │  • Join 3 modules into complete profiles│
   │  • Filter out incomplete records        │
   └──────────────────┬──────────────────────┘
                      │
                      ▼
3. MATCHING LAYER
   ┌─────────────────────────────────────────┐
   │  For Each Client Profile:               │
   │  • Claude evaluates against criteria    │
   │  • Returns: eligible/not + reasons      │
   │  • Assigns confidence score (0-100)     │
   │  • Batch process with rate limiting     │
   └──────────────────┬──────────────────────┘
                      │
                      ▼
4. RANKING & FILTERING
   ┌─────────────────────────────────────────┐
   │  • Sort by confidence score (high→low)  │
   │  • Group by tier (High/Medium/Low)      │
   │  • Filter out non-eligible (<threshold) │
   │  • Attach match rationale per client    │
   └──────────────────┬──────────────────────┘
                      │
                      ▼
5. OUTPUT GENERATION
   ┌─────────────────────────────────────────┐
   │  PDF Generation                         │
   │  • Prism + UGA branding                 │
   │  • Ranked list with contact details     │
   │  • Match reasons + missing fields       │
   │  • Account Executive assignments        │
   └──────────────────┬──────────────────────┘
                      │
                      ▼
6. DELIVERY
   ┌─────────────────────────────────────────┐
   │  Email to UGA Leadership                │
   │  • Recipient: Elias Tacher              │
   │  • Attachment: Ranked matches PDF       │
   │  • Subject: "SDRP Matches - [Date]"     │
   └─────────────────────────────────────────┘
```

---

## Phase-by-Phase Implementation Plan

### Phase 1: CRM API Evaluation ✅ **COMPLETE**

**Status:** Completed May 12, 2026
**Deliverable:** Zoho CRM Data Analysis Report (40 pages)

**Key Findings:**
- ✅ Zoho CRM API accessible and functional
- ✅ 921 Accounts, 919 Contacts, 213 Farms analyzed
- ✅ 213 farms have sufficient SDRP-specific data (matchable universe)
- ✅ 58.7% average fill rate on critical SDRP fields
- ⚠️ Critical gaps: citizenship, AD-1026, ownership %, exact coverage %
- ✅ **Recommendation:** Proceed with Phase 2 - feasible with 213 matchable farms

**Reusable Assets Built:**
- `ZohoCRMClient` class - fetch from any Zoho module
- `DataQualityAnalyzer` class - assess field completeness
- Data quality framework for future programs

---

### Phase 2: Matching Engine Build (23 hours - TO DO)

#### Step 1: Program Criteria Extraction (3 hours)

**Goal:** Transform SDRP PDF into structured, machine-readable eligibility criteria

**Approach:**

```python
# Conceptual flow - no actual code yet

def extract_program_criteria(pdf_path):
    """
    Use Claude to extract eligibility criteria from program PDF
    Returns structured criteria ready for matching
    """

    # 1. Read PDF content
    pdf_text = extract_text_from_pdf(pdf_path)

    # 2. Send to Claude with specialized prompt
    prompt = f"""
    You are an expert at analyzing USDA grant program eligibility criteria.

    Analyze this program document and extract:

    1. HARD REQUIREMENTS (must-have, binary pass/fail):
       - Citizenship/residency
       - Geographic location rules
       - Disaster event requirements
       - Conservation compliance
       - Duplicate benefit exclusions

    2. TIER 1 INDICATORS (strong qualification signals):
       - Insurance indemnity/NAP payment received
       - Named disaster event match
       - Ownership share at risk
       - Specialty crop classification

    3. TIER 2 INDICATORS (moderate signals):
       - Crop insurance coverage level
       - AGI from farming percentage
       - Tree/vine/bush losses
       - Stage 2 shallow loss eligibility

    4. TIER 3 DETAILS (administrative requirements):
       - Forms required (AD-1026, CCC-902, etc.)
       - Documentation needed
       - Application deadlines

    For each criterion, specify:
    - Field name to check in CRM
    - Expected value or condition
    - Weight/importance (critical/high/medium/low)
    - How to handle missing data

    Return as structured JSON.

    Program Document:
    {pdf_text}
    """

    # 3. Get structured criteria from Claude
    criteria = call_claude_api(
        prompt=prompt,
        model="claude-sonnet-4.5",
        cache=True  # Cache this for all subsequent client calls
    )

    # 4. Validate and structure
    return parse_criteria_response(criteria)
```

**Output Example:**

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
      "qualifying_events": ["hurricane", "wildfire", "flood", "drought", "..."],
      "weight": "critical",
      "missing_data_action": "exclude"
    }
  ],
  "tier_1_indicators": [...],
  "tier_2_indicators": [...],
  "tier_3_requirements": [...]
}
```

**Prompt Caching Strategy:**
- Store program criteria in Claude's prompt cache
- Reuse for all 500+ client evaluations
- Reduces input token cost by 90%
- Cache TTL: 5 minutes (sufficient for batch processing)

**Cost:** ~$0.10 for criteria extraction (one-time per program)

---

#### Step 2: Client Data Assembly (2 hours)

**Goal:** Fetch and join Accounts, Contacts, Farms into complete client profiles

**Approach:**

```python
# Conceptual flow

def assemble_client_profiles():
    """
    Pull all client data from Zoho CRM
    Join Accounts → Contacts → Farms
    Return list of complete profiles
    """

    # 1. Fetch all Farms records (our matchable universe)
    zoho_client = ZohoCRMClient()  # ← Already built!
    farms = zoho_client.get_all_records("Farms")

    # 2. For each farm, join to Account and Contact
    profiles = []
    for farm in farms:
        account_id = farm.get("Account_TEST")

        # Get account details
        account = zoho_client.get_record("Accounts", account_id)

        # Get associated contact
        contact = zoho_client.get_record_by_field(
            "Contacts",
            "Account_Name",
            account["Account_Name"]
        )

        # Combine into single profile
        profile = {
            "client_id": account_id,
            "company_name": account["Account_Name"],
            "contact_name": contact["Full_Name"] if contact else "Unknown",
            "email": contact["Email"] if contact else None,
            "phone": contact["Phone"] if contact else account.get("Phone"),
            "account_executive": farm["Farm_Executive"],

            # SDRP-specific fields from Farm
            "farm_state": farm["Farm_State"],
            "county": farm.get("County"),
            "disaster_event": farm.get("Loss_Cause_2023_2024"),
            "insurance_coverage": farm.get("Insurance_or_NAP_Coverage_2023_2024"),
            "insurance_type": farm.get("Type_of_Crop_Insurance_2024_2023"),
            "loss_payments": farm.get("Loss_Payments_Year_s"),
            "block_grant_state": farm.get("CT_HI_ME_MA_Losses"),
            "agi_75_percent": farm.get("AGI_900K_75_Farm_Income"),
            "crop_type": farm.get("What_They_Produce"),
            "tree_vine_losses": farm.get("Losses_Crops_Trees_Vines_2023_2024"),
            "specialty_crop": account.get("Farm_Grows_Produces_Specialty_crops"),

            # All raw data for Claude
            "raw_account": account,
            "raw_contact": contact,
            "raw_farm": farm
        }

        profiles.append(profile)

    # 3. Filter out profiles with critical missing data
    valid_profiles = [
        p for p in profiles
        if p["farm_state"] and p["farm_state"] not in ["CT", "HI", "ME", "MA"]
    ]

    return valid_profiles
```

**Data Quality Handling:**

Based on our Phase 1 analysis, we know:
- 213 farms have SDRP-specific data (our universe)
- ~125 farms have ≥50% critical fields (high confidence candidates)
- ~50-80 farms have 30-49% fields (medium confidence)

**Pre-filtering Strategy:**
- Exclude farms in block grant states (CT, HI, ME, MA)
- Exclude farms with no disaster event data
- Flag farms missing critical fields but still process them
- Include data completeness % in output for transparency

**Output:** List of 200-213 client profiles ready for matching

---

#### Step 3: Individual Client Matching Logic (8 hours)

**Goal:** For each client, use Claude to evaluate eligibility and generate match assessment

**Core Matching Prompt Architecture:**

```python
# Conceptual flow

def match_client_to_program(client_profile, program_criteria):
    """
    Use Claude to evaluate one client against program criteria
    Returns eligibility decision + confidence + reasoning
    """

    prompt = f"""
    You are an expert USDA grant eligibility analyst.

    Your task: Evaluate whether this client qualifies for the {program_criteria['program_name']} program.

    PROGRAM CRITERIA:
    {json.dumps(program_criteria, indent=2)}

    CLIENT PROFILE:
    Company: {client_profile['company_name']}
    Location: {client_profile['farm_state']}, {client_profile['county']}
    Disaster Event: {client_profile['disaster_event']}
    Insurance Coverage: {client_profile['insurance_coverage']}
    Loss Payments: {client_profile['loss_payments']}
    Crop Type: {client_profile['crop_type']}
    [... include all relevant fields ...]

    Data Completeness: {calculate_completeness(client_profile)}%

    EVALUATION INSTRUCTIONS:

    1. HARD REQUIREMENTS CHECK:
       For each hard requirement, determine:
       - Does the client meet it? (Yes/No/Unknown)
       - What data supports this?
       - What data is missing?

       If ANY hard requirement is "No", the client is INELIGIBLE.
       If ANY hard requirement is "Unknown" due to missing data, FLAG for manual review.

    2. TIER 1 INDICATORS SCORING:
       Count how many Tier 1 indicators the client meets.
       More Tier 1 matches = stronger candidate.

    3. TIER 2 INDICATORS SCORING:
       Count how many Tier 2 indicators the client meets.
       These are tie-breakers between similar candidates.

    4. CONFIDENCE SCORE (0-100):
       - 80-100: High confidence (meets all hard requirements + multiple Tier 1 indicators + good data completeness)
       - 60-79: Medium confidence (meets hard requirements + some Tier 1 indicators OR missing some data)
       - 40-59: Low confidence (meets hard requirements but limited data or weak indicators)
       - 0-39: Not eligible or insufficient data

    5. MATCH RATIONALE:
       Write 2-3 sentences explaining:
       - Why this client qualifies (or doesn't)
       - Key strengths of the match
       - Any red flags or missing data

    6. MISSING CRITICAL FIELDS:
       List any fields needed for full assessment that are empty in the CRM.

    RESPOND IN THIS EXACT JSON FORMAT:
    {{
      "eligible": true/false,
      "confidence_score": 0-100,
      "tier": "High" / "Medium" / "Low" / "Not Eligible",
      "hard_requirements_met": {{
        "citizenship": "Yes/No/Unknown",
        "geographic_location": "Yes/No/Unknown",
        "disaster_event": "Yes/No/Unknown",
        ...
      }},
      "tier_1_count": 0-4,
      "tier_2_count": 0-5,
      "match_rationale": "Brief explanation here...",
      "missing_fields": ["field1", "field2"],
      "recommended_action": "Contact immediately" / "Verify eligibility" / "Low priority" / "Not eligible"
    }}
    """

    # Call Claude with cached program criteria
    response = call_claude_api(
        prompt=prompt,
        model="claude-sonnet-4.5",
        use_cache=True,  # Program criteria cached from Step 1
        max_tokens=1000
    )

    # Parse JSON response
    match_result = json.loads(response)

    # Attach client info to result
    match_result["client_id"] = client_profile["client_id"]
    match_result["company_name"] = client_profile["company_name"]
    match_result["contact_name"] = client_profile["contact_name"]
    match_result["email"] = client_profile["email"]
    match_result["phone"] = client_profile["phone"]
    match_result["account_executive"] = client_profile["account_executive"]

    return match_result
```

**Batch Processing Strategy:**

```python
# Conceptual flow

def match_all_clients(client_profiles, program_criteria):
    """
    Process all clients with rate limiting and error handling
    """

    results = []

    for i, client in enumerate(client_profiles):
        try:
            print(f"Processing {i+1}/{len(client_profiles)}: {client['company_name']}")

            # Match client
            result = match_client_to_program(client, program_criteria)
            results.append(result)

            # Rate limiting (Claude allows ~50 requests/min for paid tier)
            if i % 50 == 0 and i > 0:
                time.sleep(60)  # Pause after every 50 requests

        except Exception as e:
            # Log error and continue
            print(f"Error processing {client['company_name']}: {e}")
            results.append({
                "client_id": client["client_id"],
                "company_name": client["company_name"],
                "eligible": False,
                "error": str(e),
                "tier": "Error"
            })

    return results
```

**Error Handling:**
- If Claude API fails: Retry once, then log and continue
- If JSON parsing fails: Default to "manual review required"
- If rate limit hit: Exponential backoff
- All errors logged with client ID for follow-up

**Cost Per Client:**
- Input: ~2,500 tokens (1,500 criteria cached + 1,000 client profile) = $0.003
- Output: ~500 tokens = $0.0075
- **Total per client: ~$0.01**
- **213 clients: ~$2.13** (with prompt caching)
- **Without caching: ~$6-8**

---

#### Step 4: Ranking & Filtering (2 hours)

**Goal:** Sort matched clients by confidence score and group into tiers

**Approach:**

```python
# Conceptual flow

def rank_and_filter_matches(match_results):
    """
    Sort, group, and prepare final match list for PDF
    """

    # 1. Filter out non-eligible
    eligible = [r for r in match_results if r.get("eligible") == True]

    # 2. Sort by confidence score (high to low)
    ranked = sorted(eligible, key=lambda x: x["confidence_score"], reverse=True)

    # 3. Group into tiers
    high_confidence = [r for r in ranked if r["confidence_score"] >= 80]
    medium_confidence = [r for r in ranked if 60 <= r["confidence_score"] < 80]
    low_confidence = [r for r in ranked if 40 <= r["confidence_score"] < 60]

    # 4. Generate summary statistics
    summary = {
        "total_clients_evaluated": len(match_results),
        "eligible_clients": len(eligible),
        "high_confidence_matches": len(high_confidence),
        "medium_confidence_matches": len(medium_confidence),
        "low_confidence_matches": len(low_confidence),
        "not_eligible": len([r for r in match_results if not r.get("eligible")]),
        "errors": len([r for r in match_results if "error" in r])
    }

    return {
        "summary": summary,
        "high_confidence": high_confidence,
        "medium_confidence": medium_confidence,
        "low_confidence": low_confidence,
        "all_ranked": ranked
    }
```

**Output Structure:**

```json
{
  "summary": {
    "total_clients_evaluated": 213,
    "eligible_clients": 142,
    "high_confidence_matches": 87,
    "medium_confidence_matches": 42,
    "low_confidence_matches": 13,
    "not_eligible": 71
  },
  "high_confidence": [
    {
      "company_name": "Smith Family Farms",
      "contact_name": "John Smith",
      "phone": "555-0100",
      "email": "john@smithfarms.com",
      "account_executive": "Allan Vargas",
      "confidence_score": 95,
      "tier": "High",
      "match_rationale": "Strong match: Received insurance indemnity for 2023 wildfire losses in California. Farm grows specialty crops (tree nuts). All hard requirements met.",
      "missing_fields": ["Citizenship_Status", "AD_1026_On_File"],
      "recommended_action": "Contact immediately"
    },
    ...
  ],
  "medium_confidence": [...],
  "low_confidence": [...]
}
```

---

#### Step 5: PDF Generation (6 hours)

**Goal:** Create branded, professional PDF with ranked matches

**PDF Structure:**

```
┌─────────────────────────────────────────────────────────────┐
│                         PAGE 1: COVER                        │
├─────────────────────────────────────────────────────────────┤
│  [Prism Logo]                              [UGA Logo]        │
│                                                               │
│              SDRP Program Match Report                       │
│              Supplemental Disaster Relief Program            │
│                                                               │
│  Generated: May 12, 2026                                     │
│  Program Year: 2023-2024 Losses                             │
│                                                               │
│  EXECUTIVE SUMMARY                                           │
│  • 213 clients evaluated                                     │
│  • 142 eligible matches found                                │
│  • 87 high-confidence recommendations                        │
│                                                               │
│  Prepared for: Elias Tacher, CEO                            │
│  Prepared by: Prism Digital Labs                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    PAGE 2: HOW TO USE THIS REPORT            │
├─────────────────────────────────────────────────────────────┤
│  CONFIDENCE LEVELS EXPLAINED                                 │
│                                                               │
│  🟢 HIGH CONFIDENCE (80-100)                                 │
│     Client meets all hard requirements and has strong        │
│     indicators (insurance indemnity, disaster event match).  │
│     RECOMMENDED ACTION: Contact immediately.                 │
│                                                               │
│  🟡 MEDIUM CONFIDENCE (60-79)                                │
│     Client meets requirements but missing some data or has   │
│     weaker indicators.                                        │
│     RECOMMENDED ACTION: Verify eligibility before contact.   │
│                                                               │
│  🟠 LOW CONFIDENCE (40-59)                                   │
│     Client may qualify but significant data gaps exist.      │
│     RECOMMENDED ACTION: Gather additional info first.        │
│                                                               │
│  PRIORITY ORDER                                              │
│  Clients are ranked highest to lowest confidence within      │
│  each tier. Start at the top and work your way down.        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              PAGE 3+: HIGH CONFIDENCE MATCHES                │
├─────────────────────────────────────────────────────────────┤
│  🟢 HIGH CONFIDENCE MATCHES (87 clients)                     │
│                                                               │
│  ─────────────────────────────────────────────────────────  │
│  #1 │ CONFIDENCE: 95                                         │
│  ─────────────────────────────────────────────────────────  │
│  Company:         Smith Family Farms                         │
│  Contact:         John Smith                                 │
│  Phone:           555-0100                                   │
│  Email:           john@smithfarms.com                        │
│  Account Exec:    Allan Vargas                               │
│                                                               │
│  WHY THEY MATCH:                                             │
│  Strong match: Received insurance indemnity for 2023         │
│  wildfire losses in California. Farm grows specialty crops   │
│  (tree nuts). All hard requirements met. Estimated high      │
│  payment potential due to specialty crop classification.     │
│                                                               │
│  MISSING DATA:                                               │
│  • Citizenship status (assumed eligible, verify)             │
│  • AD-1026 conservation compliance (verify on file)          │
│                                                               │
│  ─────────────────────────────────────────────────────────  │
│  #2 │ CONFIDENCE: 93                                         │
│  ─────────────────────────────────────────────────────────  │
│  [Next client...]                                            │
│                                                               │
└─────────────────────────────────────────────────────────────┘

[Continue for all high confidence matches]

┌─────────────────────────────────────────────────────────────┐
│            PAGE N: MEDIUM CONFIDENCE MATCHES                 │
├─────────────────────────────────────────────────────────────┤
│  🟡 MEDIUM CONFIDENCE MATCHES (42 clients)                   │
│  [Same format as high confidence]                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│             PAGE N+1: LOW CONFIDENCE MATCHES                 │
├─────────────────────────────────────────────────────────────┤
│  🟠 LOW CONFIDENCE MATCHES (13 clients)                      │
│  [Same format, note additional verification needed]          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    FINAL PAGE: APPENDIX                      │
├─────────────────────────────────────────────────────────────┤
│  DATA QUALITY NOTES                                          │
│  • 213 farms evaluated (23% of total 921 accounts)          │
│  • 71 clients excluded due to:                              │
│    - Block grant state location (CT/HI/ME/MA)               │
│    - No disaster event recorded                              │
│    - Insufficient data for assessment                        │
│                                                               │
│  NEXT STEPS                                                  │
│  1. Assign high-confidence clients to AE teams              │
│  2. Verify missing fields for medium-confidence clients     │
│  3. Update CRM with eligibility status                      │
│                                                               │
│  Questions? Contact: bhuvana@prismdigitallabs.com           │
└─────────────────────────────────────────────────────────────┘
```

**Technical Implementation:**

```python
# Conceptual flow

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf_report(ranked_matches, output_path):
    """
    Generate branded PDF from ranked match results
    """

    # 1. Initialize PDF
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # 2. Cover page
    story.append(generate_cover_page(ranked_matches["summary"]))

    # 3. Instructions page
    story.append(generate_instructions_page())

    # 4. High confidence matches
    for i, match in enumerate(ranked_matches["high_confidence"], 1):
        story.append(generate_match_card(match, rank=i, tier="High"))

    # 5. Medium confidence matches
    for i, match in enumerate(ranked_matches["medium_confidence"], 1):
        story.append(generate_match_card(match, rank=i, tier="Medium"))

    # 6. Low confidence matches
    for i, match in enumerate(ranked_matches["low_confidence"], 1):
        story.append(generate_match_card(match, rank=i, tier="Low"))

    # 7. Appendix
    story.append(generate_appendix(ranked_matches["summary"]))

    # 8. Build PDF
    doc.build(story)
```

**Branding Elements:**
- Prism logo (top left)
- UGA logo (top right)
- Color scheme: Professional blues/grays
- Consistent typography
- Footer with page numbers + "Generated by Prism Digital Labs"

**File Naming:**
`SDRP_Matches_2026-05-12.pdf`

---

#### Step 6: Email Delivery (2 hours)

**Goal:** Send PDF to Elias Tacher's email automatically

**Email Template:**

```
To: elias@unitedgrantsofamerica.com
Cc: [Optional: Allan, Philip]
Subject: SDRP Match Report - 142 Eligible Clients Identified

Hi Elias,

Attached is your SDRP program match report generated from UGA's Zoho CRM database.

KEY FINDINGS:
• 213 clients evaluated
• 142 eligible matches found
• 87 high-confidence recommendations ready for immediate contact

WHAT'S INSIDE:
The PDF is organized by confidence level (High → Medium → Low) with the strongest
matches listed first. Each entry includes:
  - Client company and contact details
  - Account Executive assignment
  - Why they match (eligibility rationale)
  - Any missing data that should be verified

RECOMMENDED NEXT STEPS:
1. Assign high-confidence clients to your AE team
2. Start with matches ranked #1-20 for fastest wins
3. Verify missing fields (citizenship, AD-1026) before application submission

Questions or need the data in a different format? Reply to this email.

---
Generated by Prism Digital Labs
Engagement 4: Program-Client Matching Engine POC
```

**Technical Implementation:**

```python
# Conceptual flow

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def send_pdf_email(pdf_path, recipient, summary):
    """
    Send PDF report via email
    """

    # Email configuration (from .env)
    sender = os.getenv("EMAIL_FROM")
    smtp_server = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_password = os.getenv("SMTP_PASSWORD")

    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = f"SDRP Match Report - {summary['eligible_clients']} Eligible Clients Identified"

    # Email body
    body = generate_email_body(summary)
    msg.attach(MIMEText(body, 'plain'))

    # Attach PDF
    with open(pdf_path, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename={os.path.basename(pdf_path)}'
        )
        msg.attach(part)

    # Send email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender, smtp_password)
        server.send_message(msg)

    print(f"✅ Email sent to {recipient}")
```

**Email Service Options:**
- **Option A**: Gmail SMTP (simple, free, good for POC)
- **Option B**: SendGrid (reliable, scalable, $15/month for 40k emails)
- **Option C**: AWS SES (enterprise, $0.10 per 1,000 emails)

**Recommendation:** Start with Gmail SMTP for POC, migrate to SendGrid if volume increases.

---

## System Architecture Decisions

### 1. Serverless vs. Hosted

**Decision: Serverless (On-Demand Execution)**

**Why:**
- No continuously running infrastructure = $0 hosting cost
- Runs only when triggered (3-4 times per year for UGA)
- No servers to maintain, monitor, or patch
- Entire system is code that lives in GitHub

**How It Works:**
- AE or UGA team member runs Python script: `python run_matching.py --program SDRP`
- Script executes, processes 500 clients, generates PDF, sends email
- Process completes in ~15-20 minutes
- Script exits, nothing left running

**Alternative Considered:**
- Scheduled cloud function (AWS Lambda, Google Cloud Functions)
- **Rejected because:** Adds complexity for 3-4 runs per year
- Can be added later if needed

---

### 2. Prompt Caching Strategy

**Decision: Cache program criteria, not client profiles**

**Why:**
- Program criteria: ~1,500 tokens, identical for all 500 clients → cache it
- Client profiles: ~1,000 tokens each, all different → don't cache
- 90% reduction in input token cost = $6 savings per run

**How Claude Prompt Caching Works:**
```python
# First call (stores criteria in cache)
response = client.messages.create(
    model="claude-sonnet-4.5",
    system=[
        {
            "type": "text",
            "text": program_criteria,  # This gets cached
            "cache_control": {"type": "ephemeral"}
        }
    ],
    messages=[
        {"role": "user", "content": f"Evaluate this client: {client_profile}"}
    ]
)

# Subsequent 499 calls reuse cached criteria
# Only the client profile changes each time
```

**Cost Comparison:**
- Without caching: ~500 * 2,500 input tokens = 1,250,000 tokens = $3.75
- With caching: 1,500 initial + (500 * 1,000) = 501,500 tokens = $1.50
- **Savings: $2.25 per 500-client run**

---

### 3. Error Handling & Retries

**Decision: Fail gracefully, log errors, continue processing**

**Strategy:**

```python
# Conceptual flow

def process_with_retry(client_profile):
    """
    Retry logic for API failures
    """
    max_retries = 2

    for attempt in range(max_retries):
        try:
            result = match_client_to_program(client_profile, program_criteria)
            return result

        except RateLimitError:
            # Hit Claude API rate limit - wait and retry
            time.sleep(60)
            continue

        except APIError as e:
            # Claude API error - retry once
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
            else:
                # Final attempt failed - log and return error result
                return {
                    "client_id": client_profile["client_id"],
                    "company_name": client_profile["company_name"],
                    "eligible": False,
                    "tier": "Error",
                    "error": f"API failure: {str(e)}",
                    "recommended_action": "Manual review required"
                }

        except Exception as e:
            # Unexpected error - log and continue
            return {
                "client_id": client_profile["client_id"],
                "company_name": client_profile["company_name"],
                "eligible": False,
                "tier": "Error",
                "error": f"Unexpected error: {str(e)}",
                "recommended_action": "Manual review required"
            }
```

**Failure Scenarios:**
- **Scenario 1:** Claude API is down
  - **Action:** Retry 2x with exponential backoff
  - **If still failing:** Abort run, notify user

- **Scenario 2:** 1-2 clients fail but others succeed
  - **Action:** Mark those clients as "Error", include in PDF with note
  - **Continue processing remaining clients**

- **Scenario 3:** Zoho CRM API fails
  - **Action:** Can't proceed without client data
  - **Abort run, retry entire process later**

**Logging:**
All errors logged to `logs/matching_run_[timestamp].log` for debugging

---

### 4. Rate Limiting

**Claude API Limits (Paid Tier):**
- 50 requests per minute
- 50,000 requests per day
- 40,000 tokens per minute

**Our Volume:**
- 213 clients = 213 requests
- At 50 req/min = ~4.5 minutes total processing time
- Well under limits

**Rate Limiting Strategy:**

```python
def process_with_rate_limit(clients, requests_per_minute=50):
    """
    Process clients with automatic rate limiting
    """
    results = []
    batch_size = requests_per_minute

    for i in range(0, len(clients), batch_size):
        batch = clients[i:i+batch_size]

        # Process batch
        for client in batch:
            result = match_client_to_program(client, program_criteria)
            results.append(result)

        # If more batches remain, wait 60 seconds
        if i + batch_size < len(clients):
            print(f"Processed {i+batch_size} clients, waiting 60s...")
            time.sleep(60)

    return results
```

**Conservative Approach:** Process 40 clients per minute (80% of limit) to leave headroom

---

### 5. Data Privacy & Security

**Sensitive Data Handling:**

1. **Zoho CRM Credentials:**
   - Stored in `.env` file (never committed to git)
   - OAuth tokens refreshed automatically
   - Access tokens expire after 1 hour

2. **Client Data:**
   - Loaded into memory only during processing
   - Not stored on disk except in output PDF
   - PDF stored locally or emailed, not uploaded to cloud

3. **Claude API:**
   - Client data sent to Anthropic for processing
   - Not stored by Anthropic (per their data policy)
   - No training on user data

4. **Email Delivery:**
   - PDF attachment sent via encrypted SMTP
   - TLS encryption in transit
   - Email stored in recipient's inbox only

**Best Practices:**
- Never log full client profiles (only IDs)
- Mask phone numbers in debug logs
- Redact emails from error messages
- Clear Claude API cache after processing

---

## Testing Strategy

### Phase 1: Sample Testing (20 clients)

**Goal:** Validate matching logic before full run

**Approach:**

```python
# Conceptual flow

def run_sample_test(sample_size=20):
    """
    Test matching engine on small sample
    """

    # 1. Get all client profiles
    all_clients = assemble_client_profiles()

    # 2. Select diverse sample
    sample = select_test_sample(all_clients, size=sample_size)
    # Include:
    #   - 5 high-confidence candidates (known strong matches)
    #   - 5 medium-confidence candidates
    #   - 5 edge cases (missing data, unclear eligibility)
    #   - 5 clear non-matches (for accuracy check)

    # 3. Run matching
    results = match_all_clients(sample, program_criteria)

    # 4. Manual review
    for result in results:
        print(f"\nClient: {result['company_name']}")
        print(f"Eligible: {result['eligible']}")
        print(f"Confidence: {result['confidence_score']}")
        print(f"Rationale: {result['match_rationale']}")
        print("---")

        # Prompt for manual validation
        correct = input("Is this assessment correct? (y/n): ")
        if correct.lower() != 'y':
            print("⚠️ Mismatch detected - review prompt logic")

    # 5. Calculate accuracy
    accuracy = sum(1 for r in results if r.get('manual_validation') == 'correct') / len(results)
    print(f"\n✅ Sample Test Accuracy: {accuracy*100}%")

    return accuracy >= 0.85  # Proceed to full run if ≥85% accurate
```

**Success Criteria:**
- ≥85% accuracy on sample (17/20 correct)
- No false positives (flagged eligible when clearly not)
- Reasonable confidence scores (matches human judgment)

**If Test Fails:**
- Review prompt instructions
- Adjust tier weights
- Add edge case handling
- Test again with new sample

---

### Phase 2: Full Run Validation

**After Processing All 213 Clients:**

1. **Spot Check High Confidence (Top 20):**
   - Manually review top 20 matches
   - Confirm they genuinely meet criteria
   - If 18/20 are correct → good

2. **Spot Check Medium Confidence (Random 10):**
   - Ensure they're not obviously eligible/ineligible
   - Verify gray area is accurately captured

3. **Check Error Cases:**
   - Review any clients marked "Error"
   - Ensure errors are legitimate (API failures, not logic bugs)

4. **Summary Statistics Sanity Check:**
   - Do percentages make sense? (~60-70% eligible typical for well-targeted programs)
   - Are confidence score distributions reasonable? (pyramid shape: fewer high, more medium/low)

**Final Approval:**
Before sending PDF to Elias, get sign-off from:
- Allan Vargas (knows clients well, can spot check names)
- Philip (technical review)

---

## Scalability for Future Programs

### Design Principle: Program-Agnostic Architecture

**Goal:** Add new programs without changing code

**How It Works:**

```
Current: SDRP program
  ↓
  program_criteria = extract_program_criteria("SDRP.pdf")
  ↓
  Run matching against clients
  ↓
  Output: SDRP_Matches.pdf

Future: New Program X
  ↓
  program_criteria = extract_program_criteria("ProgramX.pdf")
  ↓
  Run matching against clients (same code!)
  ↓
  Output: ProgramX_Matches.pdf
```

**No Code Changes Required:**
- Criteria extraction is dynamic (Claude reads any PDF structure)
- Matching logic adapts to criteria structure
- PDF generation uses same template
- Email delivery uses same mechanism

**Adding a New Program (5 Steps):**

1. Upload program PDF to `uploads/` folder
2. Run: `python run_matching.py --program ProgramX`
3. Script extracts criteria, matches clients, generates PDF
4. Review PDF
5. Email to Elias

**Estimated Time:** 30 minutes (mostly waiting for processing)

---

### Multi-Program Support (Future Phase)

**Enhancement:** Match clients against ALL active programs at once

**Approach:**

```python
# Future enhancement - not in Phase 2 scope

def match_all_programs():
    """
    Run matching against all active programs
    Return clients with best program match for each
    """

    # 1. Load all program criteria
    programs = [
        extract_program_criteria("SDRP.pdf"),
        extract_program_criteria("ELAP.pdf"),
        extract_program_criteria("ERP.pdf"),
        # ... etc
    ]

    # 2. For each client, find best matching program
    clients = assemble_client_profiles()

    results = []
    for client in clients:
        best_match = None
        best_score = 0

        for program in programs:
            match = match_client_to_program(client, program)
            if match["confidence_score"] > best_score:
                best_match = match
                best_match["program_name"] = program["program_name"]
                best_score = match["confidence_score"]

        if best_match:
            results.append(best_match)

    # 3. Group by program
    by_program = {}
    for result in results:
        program = result["program_name"]
        if program not in by_program:
            by_program[program] = []
        by_program[program].append(result)

    return by_program
```

**Output:** Multi-program PDF showing:
- Section 1: SDRP matches
- Section 2: ELAP matches
- Section 3: ERP matches
- Summary: Which clients match multiple programs

**Cost:** ~3-4x current cost (one API call per program per client)

---

## Cost Breakdown & Budget

### One-Time Costs (Phase 2 Build)

| Item | Hours | Rate | Cost |
|------|-------|------|------|
| Program criteria extraction | 3 hrs | $150/hr | $450 |
| Client data assembly | 2 hrs | $150/hr | $300 |
| Matching logic build | 8 hrs | $150/hr | $1,200 |
| Ranking & filtering | 2 hrs | $150/hr | $300 |
| PDF generation | 6 hrs | $150/hr | $900 |
| Email delivery setup | 2 hrs | $150/hr | $300 |
| **Total** | **23 hrs** | | **$3,450** |

### Per-Run Costs (Recurring)

| Item | Cost | Notes |
|------|------|-------|
| Claude API (500 clients) | $5-10 | With prompt caching |
| Zoho CRM API | $0 | Included in Zoho One |
| Email delivery (Gmail SMTP) | $0 | Free tier |
| Compute | $0 | Runs locally |
| **Total per run** | **$5-10** | |

**Annual Cost** (4 programs per year):
- 4 runs × $10 = **$40 per year**

**Comparison to Manual Process:**
- Manual review: 500 clients × 15 min each = 125 hours = $18,750 at $150/hr
- Automated: $10
- **Savings: $18,740 per program**

---

### ROI Calculation

**Investment:**
- Phase 2 build: $3,450 (one-time)

**Returns (conservative estimate):**
- 1 additional deal closed per program from matches that would have been missed
- Average UGA fee per closed deal: ~$5,000 (assumed)
- 4 programs per year = 4 deals = $20,000 additional revenue

**Payback Period:** First run (immediate)

**5-Year Value:**
- Additional revenue: $100,000 (20 deals × $5,000)
- Total cost: $3,450 + ($40 × 5 years) = $3,650
- **Net value: $96,350**

---

## Deployment & Handoff

### Code Repository Structure

```
UGA-matching-engine/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── crm_api/
│   │   ├── __init__.py
│   │   ├── zoho_client.py          # ✅ Already built
│   │   └── data_quality_analysis.py # ✅ Already built
│   │
│   ├── matching_engine/             # 🔨 To build in Phase 2
│   │   ├── __init__.py
│   │   ├── criteria_extractor.py   # Step 1: PDF → structured criteria
│   │   ├── client_assembler.py     # Step 2: Zoho data → profiles
│   │   ├── matcher.py               # Step 3: Core matching logic
│   │   └── ranker.py                # Step 4: Sort & filter
│   │
│   ├── pdf_generator/               # 🔨 To build in Phase 2
│   │   ├── __init__.py
│   │   ├── report_builder.py       # Step 5: Create PDF
│   │   └── templates/               # PDF layout templates
│   │       └── match_report.py
│   │
│   └── email_service/               # 🔨 To build in Phase 2
│       ├── __init__.py
│       └── sender.py                # Step 6: Email delivery
│
├── uploads/                         # Program PDFs go here
│   └── .gitkeep
│
├── outputs/                         # Generated PDFs saved here
│   └── .gitkeep
│
├── logs/                            # Processing logs
│   └── .gitkeep
│
├── tests/                           # Unit tests
│   ├── test_matcher.py
│   └── test_pdf_generator.py
│
├── docs/
│   ├── ZOHO_CRM_DATA_ANALYSIS.md   # ✅ Already created
│   ├── MATCHING_ENGINE_DESIGN.md   # ✅ This document
│   └── USER_GUIDE.md                # 🔨 To create in Phase 2
│
└── run_matching.py                  # 🔨 Main entry point (Phase 2)
```

### Main Entry Point

```python
# run_matching.py - Phase 2 to build

"""
UGA Matching Engine - Main Entry Point

Usage:
    python run_matching.py --program SDRP

Options:
    --program NAME      Program name (matches PDF filename)
    --sample SIZE       Run on sample of N clients (for testing)
    --output PATH       Custom output directory
    --email RECIPIENT   Override default email recipient
"""

import argparse
from src.matching_engine.criteria_extractor import extract_program_criteria
from src.matching_engine.client_assembler import assemble_client_profiles
from src.matching_engine.matcher import match_all_clients
from src.matching_engine.ranker import rank_and_filter_matches
from src.pdf_generator.report_builder import generate_pdf_report
from src.email_service.sender import send_pdf_email

def main():
    parser = argparse.ArgumentParser(description="UGA Program-Client Matching Engine")
    parser.add_argument("--program", required=True, help="Program name")
    parser.add_argument("--sample", type=int, help="Sample size for testing")
    args = parser.parse_args()

    print(f"🚀 Starting matching engine for {args.program}")

    # Step 1: Extract program criteria
    print("📄 Extracting program criteria from PDF...")
    criteria = extract_program_criteria(f"uploads/{args.program}.pdf")

    # Step 2: Assemble client profiles
    print("👥 Fetching client data from Zoho CRM...")
    clients = assemble_client_profiles()

    if args.sample:
        clients = clients[:args.sample]
        print(f"📊 Using sample of {args.sample} clients for testing")

    # Step 3: Match clients
    print(f"🔍 Matching {len(clients)} clients against {args.program} criteria...")
    matches = match_all_clients(clients, criteria)

    # Step 4: Rank and filter
    print("📊 Ranking matches by confidence...")
    ranked = rank_and_filter_matches(matches)

    # Step 5: Generate PDF
    print("📑 Generating PDF report...")
    pdf_path = generate_pdf_report(ranked, f"outputs/{args.program}_Matches_{date.today()}.pdf")

    # Step 6: Send email
    print("📧 Sending email to UGA team...")
    send_pdf_email(pdf_path, os.getenv("EMAIL_TO_ELIAS"), ranked["summary"])

    print(f"✅ Complete! {ranked['summary']['eligible_clients']} matches found.")
    print(f"📄 PDF saved to: {pdf_path}")

if __name__ == "__main__":
    main()
```

---

## Maintenance & Support

### Maintenance Scenarios

| Scenario | Frequency | Effort | Cost |
|----------|-----------|--------|------|
| **Add new program** | 3-4x per year | 30 min | $75 |
| **Zoho field rename** | Rare (1-2x per year) | 1 hour | $150 |
| **Claude API version upgrade** | 1x per year | 2 hours | $300 |
| **PDF template update** | Rare (as needed) | 2 hours | $300 |
| **Bug fix / enhancement** | As needed | 1-4 hours | $150-600 |

**Average Annual Maintenance:** ~$500-1,000 (conservatively)

### Optional Retainer

**Tier 1: Basic Support**
- 2 hours per month ($300/month)
- Covers: new program additions, minor bug fixes, monitoring
- No minimum commitment

**Tier 2: Enhanced Support**
- 5 hours per month ($750/month)
- Covers: Basic + enhancements, RingSense integration, document search
- Rollover unused hours (max 10 hours)

**Tier 3: Ad-Hoc**
- No retainer
- Bill hourly as needed ($150/hr)
- 48-hour response SLA

**Recommendation for UGA:** Start with Tier 3 (ad-hoc) since this is low-maintenance system

---

## Future Enhancements Roadmap

### Phase 3: Document & Attachment Search (TBD)

**Goal:** Enrich matching with unstructured data from Zoho CRM attachments and Zoho Projects documents

**Approach:**
1. Query Zoho CRM attachments (902 forms, intake docs)
2. Extract text from PDFs using OCR
3. Feed extracted text to Claude alongside CRM fields
4. More complete client profile = better matching accuracy

**Estimated Effort:** 10-15 hours
**Value:** Increases match confidence, reduces "missing data" flags

---

### Phase 4: RingSense AI Transcript Integration (TBD)

**Goal:** Extract client context from AE call transcripts to supplement CRM data

**Approach:**
1. Connect to RingCentral Conversation Expert API
2. Fetch transcripts for each client
3. Use Claude to extract eligibility-relevant details from transcripts
4. Add to client profile before matching

**Example:**
- Transcript mentions: "Client said they lost 50 acres to wildfire in 2023"
- System extracts: disaster_event="wildfire", disaster_year="2023", loss_amount="50 acres"
- Uses this to fill CRM gaps

**Estimated Effort:** 15-20 hours (includes RingCentral API approval process)
**Value:** Preserves institutional knowledge from AE calls, especially critical when AEs leave

---

### Phase 5: Scheduled Automation (TBD)

**Goal:** Run matching automatically on a schedule without manual trigger

**Approach:**
1. Deploy as AWS Lambda function or Google Cloud Function
2. Schedule: 1st of each month
3. Process all active programs
4. Deliver PDFs to Elias automatically

**Estimated Effort:** 5-8 hours
**Value:** Zero-touch operation, Elias gets updated matches monthly

---

### Phase 6: Multi-Program Optimization (TBD)

**Goal:** Match each client to their BEST program, not just all programs

**Approach:**
1. Run matching against all UGA programs
2. Calculate which program maximizes client's potential payout
3. Recommend optimal program per client
4. Include secondary/tertiary matches

**Estimated Effort:** 8-12 hours
**Value:** Maximizes revenue per client relationship

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Claude API unavailable during run** | Low | High | Retry logic + manual fallback |
| **Zoho CRM field structure changes** | Medium | Medium | Field mapping config file, easy to update |
| **Client data quality too poor** | Low | High | Already validated in Phase 1 - 213 farms have good data |
| **Matching accuracy below expectations** | Medium | High | Sample testing before full run + manual review step |
| **PDF generation errors** | Low | Medium | Extensive testing + fallback to simple text output |
| **Email delivery fails** | Low | Low | Log failure, save PDF locally, manual send as backup |
| **Cost overruns (Claude API)** | Low | Low | Prompt caching limits cost to $10 max; abort if approaching $20 |

**Overall Risk Level:** Low - All major risks have clear mitigation strategies

---

## Success Metrics

### Phase 2 Completion Criteria

**Must-Have:**
- [ ] Program criteria successfully extracted from SDRP PDF
- [ ] All 213 farm client profiles assembled from Zoho
- [ ] Matching logic tested on 20-client sample with ≥85% accuracy
- [ ] Full 213-client run completes without critical errors
- [ ] PDF generated with correct branding and ranked list
- [ ] PDF delivered to Elias's email
- [ ] Elias confirms report is readable and actionable

**Nice-to-Have:**
- [ ] ≥90% of eligible clients flagged correctly
- [ ] <5% of non-eligible clients incorrectly flagged eligible
- [ ] <10 clients marked as "Error" or "Manual Review Required"
- [ ] Processing completes in <30 minutes

### Post-Delivery Success

**30 Days After Delivery:**
- [ ] UGA AE team has contacted top 20 high-confidence matches
- [ ] ≥50% of contacted matches confirm eligibility
- [ ] ≥1 application submitted based on match report
- [ ] Elias approves system for use with next program

**90 Days After Delivery:**
- [ ] ≥1 deal closed from matched client
- [ ] System used for 2nd program run with <30 min setup time
- [ ] No critical bugs or blockers reported

---

## Conclusion

This matching engine design delivers on UGA's core need: **systematically identify revenue opportunities from their existing 500+ client database without relying on AE institutional knowledge.**

**Key Strengths:**
- **Lightweight:** No servers, no continuous costs, runs on-demand
- **Scalable:** Add new programs in 30 minutes without code changes
- **Cost-Effective:** $10 per run vs. $18,750 manual equivalent
- **Maintainable:** Owned by UGA, minimal vendor lock-in
- **Extensible:** Clear roadmap for RingSense, documents, scheduling

**Next Steps:**
1. Review and approve this design
2. Begin Phase 2 build (23 hours)
3. Test on SDRP sample (20 clients)
4. Run full 213-client matching
5. Deliver PDF to Elias
6. Measure results and iterate

**Questions or feedback on this design? Let's discuss before building.**

---

**Document Version:** 1.0
**Status:** Design Complete - Ready for Build Approval
**Prepared By:** Prism Digital Labs
**Date:** May 12, 2026
**Next Review:** Upon build completion

---

**END OF DESIGN DOCUMENT**
