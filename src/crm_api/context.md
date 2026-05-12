# CRM API Integration Module

**Owner**: Bhuvana Raghu

## Purpose
Fetch client data from Zoho CRM API for matching against grant programs.

## Phase 1 & 2 Requirements
- Fetch 500+ client records from Zoho CRM
- Retrieve all fields that provide information about clients and their farms
- Data needed for matching against program eligibility criteria

## API Credentials
**IMPORTANT**: Store these in `.env` file, never commit to git

```
Client ID: 1000.GMZK1W408HHUU9OI72KS7196K8M3DJ
Client Secret: 2c3873aefd7526b41ebc9d0699f0bf8535c17b9e1e
```

## Implementation Details

### Authentication
- Platform: Zoho CRM
- Auth method: OAuth 2.0 (using Client ID and Secret)
- Need to implement token refresh logic

### Data Requirements
Fetch fields related to:
- Client/company information
- Farm details and operations
- Geographic location
- Contact information (company name, point of contact, phone, email)
- Account Executive assignment
- Any eligibility-related data (citizenship, role in operations, etc.)

### API Endpoints
- Zoho CRM API documentation: https://www.zoho.com/crm/developer/docs/api/v2/
- Main endpoint for contacts/accounts retrieval
- Handle pagination for 500+ records
- Consider rate limits

### Considerations
- Rate limiting (check Zoho CRM API limits)
- Pagination handling for large dataset
- Error handling for API failures
- Caching strategy (if needed)
- Field mapping to match against eligibility criteria

## Input
- API credentials from environment variables
- Optional filters (if needed for specific client segments)

## Output
Structured list of client records with fields:
- Company name
- Point of contact name
- Phone number
- Email address
- Account Executive name
- Location/geographic data
- Farm operation details
- All other eligibility-relevant fields

Format: JSON/dict compatible with matching engine

## Dependencies
- `requests` or `httpx` for HTTP calls
- `python-dotenv` for environment variable management
- `oauthlib` or Zoho's Python SDK (if available)

## Notes
- Need to explore Zoho CRM API documentation
- Identify exact field names in Zoho for matching criteria
- Test with small batch before processing all 500+ records
- Document field mappings between Zoho and our eligibility criteria
