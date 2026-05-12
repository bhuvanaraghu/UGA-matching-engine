# UGA - Program-Client Matching Engine
## Project Overview

### Client
**United Grants of America (UGA)**

### Engagement
Engagement 4: Program <> Client Matching Engine POC

---

## Executive Summary

Build a backend matching engine that:
1. Parses grant program details from PDF files
2. Fetches client data from Zoho CRM (500+ records)
3. Matches programs to eligible clients using AI-driven criteria extraction
4. Generates branded PDF reports with ranked client matches
5. Supports both manual/API triggers and scheduled automation

---

## Phase 1 & 2 Scope

### In Scope
1. **PDF Parsing** - Extract eligibility criteria from program PDFs using Claude
2. **Zoho CRM Integration** - Fetch 500+ client records with farm/business details
3. **Matching Engine** - Match programs to clients based on eligibility criteria
4. **PDF Generation** - Create branded, ranked output PDFs
5. **API Endpoints** - Manual trigger via REST API
6. **Documentation** - Comprehensive context files for implementation

### Out of Scope (Future Phases)
- Zoho Workdrive integration (manual upload for now)
- Automated scheduling (manual trigger for Phase 1/2)
- Automated email delivery (manual send for Phase 1/2)

---

## Team & Ownership

| Module | Owner | Status |
|--------|-------|--------|
| PDF Parser (Program Eligibility Extraction) | Amanda Ford | Phase 1/2 |
| Zoho CRM API Integration | Bhuvana Raghu | Phase 1/2 |
| Matching Engine | TBD | ON HOLD (pending PDF Parser + CRM API) |
| PDF Generator | TBD | Phase 1/2 |
| API Endpoints | TBD | Phase 1/2 |
| Scheduler | - | Future Phase |
| Email Service | - | Future Phase |

### Additional Stakeholders
- **Philip** - UGA team uploads program files to Zoho
- **Elias Tacher** - Recipient of output PDFs

---

## Workflow

```
1. PROGRAM INPUT
   ↓
   [PDF files] → Manual upload to /uploads
   (Future: Auto-fetch from Zoho Workdrive)

2. PDF PARSING (Amanda Ford)
   ↓
   Claude extracts:
   - Eligibility criteria
   - Criteria strength (strong/medium/low)
   - Custom research data (e.g., disaster zones for SDRP)

3. CLIENT DATA FETCH (Bhuvana Raghu)
   ↓
   Zoho CRM API returns 500+ clients:
   - Company name, contact info
   - Farm details, location
   - Account Executive assignment

4. MATCHING ENGINE (ON HOLD)
   ↓
   For each client:
   - Check eligibility criteria
   - Calculate match strength
   - Generate match reason
   - Rank by strength

5. PDF GENERATION
   ↓
   Create branded PDF with:
   - Ranked client list (strong → weak)
   - Contact details for Account Executives
   - Match summaries

6. DELIVERY
   ↓
   Manual email to Elias Tacher
   (Future: Automated email)
```

---

## Technical Architecture

### Technology Stack
- **Language**: Python 3.9+
- **API Framework**: FastAPI (recommended)
- **PDF Parsing**: PyPDF2 / pdfplumber + Claude API
- **PDF Generation**: ReportLab / WeasyPrint
- **CRM Integration**: Zoho CRM API v2
- **Data Processing**: pandas, numpy
- **Environment**: Python venv, .env configuration

### Data Flow
```
Program PDF → PDF Parser → Eligibility Criteria (JSON)
                                    ↓
                              Matching Engine
                                    ↓
Zoho CRM → Client Records → Matching Engine → Ranked Matches
                                    ↓
                              PDF Generator → Output PDF
```

---

## Key Features

### 1. Intelligent Criteria Extraction
- Use Claude to parse unstructured program PDFs
- Extract eligibility requirements automatically
- Categorize criteria by strength (strong/medium/low indicators)
- Handle custom research (e.g., SDRP disaster zone mapping)

### 2. Scalable Matching
- Process 500+ client records
- Configurable matching algorithm
- Ranking by match strength
- Generate match explanations ("why they're a good match")

### 3. Professional Output
- Prism & UGA branded PDFs
- Clean, ranked client list
- All info needed for Account Executives to contact clients:
  - Company name
  - Point of contact
  - Phone & email
  - Account Executive name
  - Match summary

### 4. Flexible Execution
- API endpoints for manual triggering
- Future: Scheduled automation
- Future: Event-driven (new file uploads)

---

## Example: SDRP Program

### Program Requirements
- **Location**: Areas affected by named disasters in 2023-2024
- **Disaster Types**: Wildfires, hurricanes, floods, derechos, tornadoes, etc.
- **Exclusions**: CT, HI, ME, MA
- **Citizenship**: US citizens
- **Role**: Active in farm operations

### Custom Research Needed
Created comprehensive list of Named Disaster Events (2023-2024):
- Location (city, state, country)
- Event name
- Duration/date
- Reference links

Output: *2023-2024 Named natural disaster events_location table*

### Decision Point
Is custom research/inference worth it for future programs?
- **Pro**: More accurate matching, better results
- **Con**: Manual effort, not fully automated

---

## API Credentials

### Zoho CRM
```
Client ID: 1000.GMZK1W408HHUU9OI72KS7196K8M3DJ
Client Secret: 2c3873aefd7526b41ebc9d0699f0bf8535c17b9e1e
```
**⚠️ Store in `.env` file, never commit to git**

### Claude API
TBD - needed for PDF parsing

---

## Output Requirements

### PDF Content (per program)
- **Header**: Program name, generation date, Prism/UGA branding
- **Summary Stats**: Total matches, breakdown by strength
- **Ranked Client List**:
  - Contact company name
  - Point of contact name
  - Phone number
  - Email address
  - Account Executive name
  - Match strength indicator
  - Brief summary of why they're a good match

### File Naming
`{program_name}_{YYYY-MM-DD}_matches.pdf`

Example: `SDRP_2026-05-12_matches.pdf`

---

## Roadmap

### Phase 1 & 2 (Current)
- ✅ Project structure and documentation
- 🔄 PDF parser with Claude integration
- 🔄 Zoho CRM API integration
- ⏳ Matching engine (on hold)
- ⏳ PDF generator
- ⏳ API endpoints
- Manual uploads, manual email

### Future Phases
- Zoho Workdrive integration
- Automated file monitoring
- Scheduled processing (cron/scheduler)
- Automated email delivery
- Enhanced matching algorithms
- Multi-program support
- Analytics and reporting dashboard

---

## Success Metrics

### Phase 1 & 2
- Successfully parse SDRP program PDF
- Fetch all 500+ client records from Zoho CRM
- Generate accurate eligibility criteria
- Produce ranked matches with >80% accuracy
- Generate professional PDF output
- Process complete workflow end-to-end

### Future
- Process multiple programs per week
- Reduce manual intervention to <10%
- Account Executive satisfaction with match quality
- Track conversion rate (matches → closed deals)

---

## Risk & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| PDF parsing fails on complex formats | High | Test with multiple program types, fallback to manual extraction |
| Zoho CRM API rate limits | Medium | Implement caching, pagination, rate limit handling |
| Matching criteria too generic | High | Iterative refinement, feedback loop with Account Executives |
| Missing client data fields | Medium | Handle null values gracefully, flag incomplete records |
| Custom research too manual | Medium | Define threshold for automation vs. manual work |

---

## Next Steps

1. **Amanda Ford**: Begin PDF parser implementation with Claude integration
2. **Bhuvana Raghu**: Complete Zoho CRM API integration and data mapping
3. **Team**: Review data structures from both sources
4. **Team**: Design matching engine logic based on real data
5. **Team**: Create PDF template mockup for approval
6. **Team**: Build API endpoints and orchestration
7. **Team**: End-to-end testing with SDRP program
8. **Team**: Iterate based on output quality

---

## Resources

- [Zoho CRM API Documentation](https://www.zoho.com/crm/developer/docs/api/v2/)
- [Claude API Documentation](https://docs.anthropic.com/)
- Project context files in `src/*/context.md`
- SDRP program PDF (TBD - location)
- 2023-2024 disaster events table (TBD - location)

---

## Questions & Decisions Needed

1. **PDF Parser**: Which Python PDF library works best with Claude?
2. **Matching Engine**: Exact algorithm/scoring methodology?
3. **Custom Research**: Threshold for when to do custom research vs. generic parsing?
4. **Branding**: Where to get Prism/UGA logos and brand guidelines?
5. **Testing**: What constitutes "good match" for validation?
6. **Deployment**: Where will this run? (Local, cloud, container?)

---

**Document Version**: 1.0
**Last Updated**: 2026-05-12
**Author**: Prism Team
