# API Module

## Purpose
REST API endpoints for triggering matching process manually or via integrations.

## Phase 1 & 2 Requirements
Support "multiple triggers" execution model:
- API endpoints (for manual/programmatic triggering)
- Scheduled/cron jobs (for automated runs)

## Implementation Details

### Framework
- **Recommended**: FastAPI (modern, async, auto-documentation)
- Alternative: Flask

### Proposed Endpoints

#### Core Functionality
```
POST /api/match
- Trigger matching process for uploaded program PDF
- Body: { "program_file": "path/to/pdf" }
- Returns: { "job_id": "...", "status": "processing" }

GET /api/match/{job_id}
- Check status of matching job
- Returns: { "job_id": "...", "status": "completed|processing|failed", "result_pdf": "..." }

POST /api/match/bulk
- Process multiple programs at once
- Body: { "program_files": ["path1", "path2"] }
- Returns: { "job_ids": [...] }

GET /api/health
- Health check endpoint
- Returns: { "status": "healthy" }
```

#### Future Endpoints
```
GET /api/programs
- List all processed programs

GET /api/programs/{program_id}/matches
- View matches for specific program

POST /api/reprocess/{program_id}
- Rerun matching for a program
```

### Authentication
- API key authentication (for Phase 1/2)
- Future: OAuth or more sophisticated auth
- Store API keys in environment variables

### Request/Response Format
- JSON for all requests and responses
- Standard error response format
- Include timestamps and request IDs for tracking

### Error Handling
- Proper HTTP status codes
- Detailed error messages (for debugging)
- User-friendly messages (for clients)
- Logging all requests and errors

### Async Processing
- Long-running matching jobs should be async
- Return job ID immediately
- Client polls for status
- Consider implementing webhooks for completion notification (future)

## Input
- HTTP requests with program file paths or job IDs
- API authentication headers

## Output
- JSON responses with job status, results, or errors
- Links to generated PDF files

## Dependencies
- FastAPI (recommended) or Flask
- Uvicorn (ASGI server for FastAPI)
- Pydantic (data validation)
- Background task library (Celery, or FastAPI's BackgroundTasks)

## Integration with Scheduler
- API and scheduler should call same core matching logic
- Keep business logic separate from API/scheduler layers
- Both trigger same workflow, just different entry points

## Notes
- Auto-generated API documentation (FastAPI provides Swagger UI)
- Rate limiting considerations (future)
- Monitoring and logging strategy
- Consider containerization (Docker) for deployment
