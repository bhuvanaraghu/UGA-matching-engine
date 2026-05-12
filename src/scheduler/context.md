# Scheduler Module

## Purpose
Automated execution of matching process on a schedule or triggered by events.

## Phase 1 & 2 Requirements
Support "multiple triggers" execution model:
- Manual trigger (initially)
- API endpoints (see api module)
- Scheduled/automated runs (this module)

## Current Status
- **Phase 1 & 2**: Manual trigger for processing programs
- **Roadmap**: Build scheduler to auto-pick up new program document files

## Future Implementation Details

### Triggering Options

#### 1. Time-Based Scheduling
- Daily run at specific time (e.g., 2 AM)
- Weekly run (e.g., every Monday)
- Custom cron schedule

#### 2. Event-Based Triggering
- Watch for new files in Zoho Workdrive
- Process when new PDF uploaded to `uploads/` directory
- Webhook from external system

### Integration with Zoho Workdrive
- Monitor "Prism Program Matching Engine" Zoho Workdrive
- Detect new program PDF uploads
- Download and process automatically
- Mark as processed to avoid duplicates

### Scheduler Options
- **APScheduler** (Python-based, easy to use)
- **Celery + Redis/RabbitMQ** (more robust, distributed)
- **Cron** (system-level, simple)
- **Airflow** (complex workflows, overkill for Phase 1/2)

### Workflow
1. Scheduler triggers at specified time/event
2. Check for new program files
3. For each new file:
   - Parse PDF (pdf_parser)
   - Fetch client data (crm_api)
   - Run matching (matching_engine)
   - Generate PDF (pdf_generator)
   - Log results
4. Send completion notification
5. Handle errors and retries

## Configuration
- Schedule frequency (environment variable or config file)
- Source location for program files
- Notification settings (email, Slack, etc.)
- Error handling: retry logic, max retries

## Input
- Schedule configuration
- Program file location (Zoho Workdrive or local directory)

## Output
- Execution logs
- Success/failure notifications
- Metrics (programs processed, matches found, errors)

## Dependencies
- APScheduler or Celery
- Zoho Workdrive API (future)
- Notification service (email, Slack)
- Logging framework

## Monitoring & Notifications
- Log all scheduled runs
- Alert on failures
- Summary reports (daily/weekly digest)
- Track processing metrics

## Error Handling
- Retry failed jobs
- Alert on repeated failures
- Dead letter queue for problematic files
- Manual intervention triggers

## Notes
- **Phase 1 & 2**: Manual trigger, no scheduler needed initially
- **Future**: Automate with scheduler watching Zoho Workdrive
- Keep scheduler logic thin - delegate to core modules
- Consider timezone handling for scheduled runs
- Need to prevent duplicate processing of same file
