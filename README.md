# UGA - United Grants of America
## Program-Client Matching Engine

### Overview
Backend service that matches grant programs to clients by:
- Parsing program details from PDF files
- Fetching client data from CRM API
- Running matching algorithm
- Generating output PDFs
- Emailing results to clients

### Project Structure
```
UGA/
├── src/
│   ├── pdf_parser/          # Parse program PDFs
│   ├── crm_api/             # Integrate with CRM API
│   ├── matching_engine/     # Core matching logic
│   ├── pdf_generator/       # Generate output PDFs
│   ├── email_service/       # Email functionality
│   ├── api/                 # REST API endpoints
│   └── scheduler/           # Scheduled job configuration
├── tests/                   # Unit and integration tests
├── uploads/                 # Input PDF storage
├── outputs/                 # Generated PDF outputs
└── docs/                    # Documentation

```

### Technology Stack
- **Language**: Python
- **Execution**: Both API endpoints and scheduled jobs
- **Data Source**: External CRM API (no database needed)

### Getting Started
TODO: Add setup instructions once implementation details are finalized

### Documentation
See context.md files in each module directory for detailed implementation plans.
