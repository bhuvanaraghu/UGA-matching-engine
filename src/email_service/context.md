# Email Service Module

## Purpose
Send generated PDF reports to stakeholders (primarily Elias Tacher).

## Phase 1 & 2 Status
**NOT IN SCOPE** - Manual email process for Phase 1 & 2

Prism team will manually send output PDF to Elias Tacher.

## Roadmap (Future Phase)
Auto-email output PDF to Elias Tacher after generation.

## Future Implementation Details

### Recipients
- Primary: Elias Tacher (email TBD)
- Potentially: Account Executives
- Potentially: Other stakeholders

### Email Content
- Subject line: Grant program name and date
- Body: Summary of matches found
- Attachment: Generated PDF
- Professional email template

### Email Service Options
- SMTP (via Gmail, Outlook, etc.)
- SendGrid
- AWS SES
- Mailgun
- Other transactional email service

### Authentication & Configuration
- Credentials stored in environment variables
- Email templates (HTML)
- Error handling and retry logic
- Delivery confirmation

## Input (Future)
- Recipient email address(es)
- PDF file path
- Email subject and body content
- Program details for context

## Output (Future)
- Email delivery status
- Delivery confirmation
- Error logs if failed

## Dependencies (Future)
- Email service library (smtplib, sendgrid, boto3, etc.)
- Email template engine (Jinja2 or similar)
- Environment configuration

## Notes
- **Phase 1 & 2**: This module is NOT needed - manual email process
- **Future phase**: Implement automated email delivery
- Need to determine email service provider
- Consider email tracking/analytics for delivery confirmation
