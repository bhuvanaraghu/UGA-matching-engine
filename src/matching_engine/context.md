# Matching Engine Module

**Status**: ON HOLD until PDF Parser & CRM API integration are complete

## Purpose
Core business logic that matches grant programs to eligible clients based on extracted criteria.

## Phase 1 & 2 Requirements
- Run eligibility criteria against every single client record from Zoho CRM
- Determine which clients are eligible vs. not eligible
- Rank eligible clients by match strength

## Implementation Details

### High-Level Process
1. Receive program eligibility criteria (from PDF Parser)
2. Receive all client records (from CRM API)
3. For each client:
   - Check against all eligibility criteria
   - Calculate match strength
   - Generate match reason/summary
4. Rank clients by match strength
5. Output ranked list for PDF generation

### Matching Criteria (Examples)
Based on SDRP program, criteria may include:
- **Location**: Geographic matching (city, state, disaster zones)
- **Disaster impact**: Named disaster events in client location
- **Citizenship**: US citizen requirement
- **Role in farm operations**: Active role verification
- **Program-specific criteria**: Custom per program

### Ranking System
Clients should be ranked based on:
- **Strong match**: Meets all or most strong indicators
- **Medium match**: Meets medium indicators, may miss some strong ones
- **Weak match**: Meets minimum criteria only

Each match needs:
- Match score/strength
- Brief summary of WHY they're a good match
- Which criteria they meet

### Edge Cases to Handle
- Client meets no criteria (exclude from output)
- Client partially meets criteria (include with lower ranking)
- Missing data in client record (how to handle?)
- Multiple programs per client (future consideration)

## Input
- **Program eligibility criteria** (from PDF Parser):
  - List of criteria with strength weights (strong/medium/low)
  - Special conditions or custom data
- **Client data** (from CRM API):
  - All 500+ client records with relevant fields

## Output
Ranked list of matching clients with:
- Client company name
- Point of contact name
- Phone number
- Email address
- Account Executive name
- Match strength/score
- Brief summary of why they're a good match
- Criteria they meet

Format: Sorted list (JSON/dict) ready for PDF generation

## Dependencies
- Data processing libraries (pandas, numpy)
- Potentially: fuzzy matching libraries for location/text matching
- Logic framework (no ML needed for Phase 1/2)

## Notes
- **HOLD**: Need PDF Parser and CRM API complete first
- Design implementation plan after seeing actual data structures
- May need to iterate on ranking algorithm based on initial results
- Consider creating detailed matching report for review before PDF generation
