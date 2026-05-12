# PDF Parser Module

**Owner**: Amanda Ford

## Purpose
Parse program details from uploaded PDF files and extract eligibility criteria for matching clients to grant programs.

## Phase 1 & 2 Requirements
- Process SDRP program PDF files (provided)
- Accept new program PDF files ad hoc
- Solution must be reusable for most programs without customization
- Use Claude with prompts to extract eligibility criteria

## Implementation Details

### Eligibility Criteria to Extract
- Location requirements
- Disaster-related criteria (for programs like SDRP)
- Citizenship requirements (e.g., US citizen)
- Role in farm operations
- Any other program-specific criteria

### Matching & Ranking Criteria
Extract and categorize criteria strength:
- **Strong indicators** (X criteria)
- **Medium indicators** (Y criteria)
- **Low indicators** (Z criteria)

### Special Cases (SDRP Example)
Some programs require custom research/inference:
- SDRP required researching Named Disaster Events (2023-2024)
- Events: wildfires, hurricanes, floods, derechos, excessive heat, tornadoes, winter storms, freeze, smoke exposure, excessive moisture, qualifying drought
- Excluded states: Connecticut, Hawaii, Maine, Massachusetts
- Output format: Location (city, state, country), event name, duration/date, reference links
- Reference: [2023-2024 Named natural disaster events_location table]

**Decision needed**: Is custom research/inference worth it for future programs?

## Input
- PDF files (initially from manual upload, future: Zoho Workdrive "Prism Program Matching Engine")
- Currently manual trigger
- Roadmap: Scheduler to auto-pick up new files

## Output
Structured eligibility criteria including:
- List of all criteria
- Criteria strength/weight (strong/medium/low)
- Special conditions or custom research data
- Format: JSON/dict for matching engine

## Dependencies
- PDF parsing library (PyPDF2, pdfplumber, or similar)
- Claude API for intelligent extraction
- Future: Zoho Workdrive API integration

## Notes
- Most programs should work with reusable solution
- Some programs may need custom research (like SDRP disaster data)
- Need to decide on threshold for custom work
