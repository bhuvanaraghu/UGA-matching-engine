# PDF Generator Module

## Purpose
Generate branded, ranked output PDF files containing eligible clients for each grant program.

## Phase 1 & 2 Requirements
- Create clean, professional PDF output
- Prism and UGA branded design
- Ranked list of matched clients (strong matches at top, weaker matches below)
- Include all required client information for Account Executives to contact clients

## Output PDF Requirements

### Required Information Per Client
1. **Contact company name**
2. **Point of contact name**
3. **Contact phone number**
4. **Contact email**
5. **Brief summary of why they're a good match**
6. **Name of Account Executive** who was on this account
7. **Ranking indicator** (strong/medium/weak match)

### Design & Branding
- Prism branding
- UGA branding
- Professional, clean layout
- Clear visual hierarchy showing ranking
- Easy to scan for Account Executives

### Organization
- Clients sorted by match strength (descending)
- Strong matches prominently displayed at top
- Clear sections or visual indicators for match strength
- Summary stats at top (total matches, breakdown by strength, etc.)

## Input
- Ranked list of matching clients (from Matching Engine)
- Program name/details for header
- Branding assets (logos, colors)

## Output
- PDF file saved to `outputs/` directory
- File naming convention: `{program_name}_{date}_matches.pdf`
- Returns file path for manual email attachment

## Implementation Considerations
- PDF library options: ReportLab, WeasyPrint, FPDF, or similar
- Template-based approach for reusability
- Handle varying numbers of matches (5 matches vs. 200 matches)
- Page breaks and pagination
- Professional typography and spacing

## Dependencies
- PDF generation library (TBD - ReportLab, WeasyPrint, etc.)
- Pillow (for image/logo handling)
- Branding assets (logos, color codes)

## Roadmap
- Phase 1/2: Manual email to Elias Tacher
- Future: Auto-email PDF to Elias Tacher (integrate with email_service module)

## Notes
- Need to get Prism and UGA logos/branding guidelines
- May want to create template mockup for approval before coding
- Consider creating both summary page and detailed client pages
- Accessibility considerations (readable fonts, good contrast)
