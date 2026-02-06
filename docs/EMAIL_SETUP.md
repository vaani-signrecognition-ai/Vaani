# Email Notification Setup Guide

## Overview
When an admin approves an NGO partnership request, the system automatically sends a professional email notification to the NGO's registered email address.

## Features
✅ **Approval Email** - Welcome message with login credentials
✅ **Rejection Email** - Polite notification (optional)
✅ **Professional HTML Design** - Beautiful, branded emails
✅ **Secure Credentials** - Temporary password for first login

## Configuration

### Step 1: Create `.env` File
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### Step 2: Configure Email Settings

#### For Gmail:
1. **Enable 2-Factor Authentication** on your Google account
2. **Generate App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password
3. **Update `.env` file**:
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-16-char-app-password
```

#### For Other Email Providers:

**Outlook/Hotmail:**
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SENDER_EMAIL=your-email@outlook.com
SENDER_PASSWORD=your-password
```

**Yahoo:**
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SENDER_EMAIL=your-email@yahoo.com
SENDER_PASSWORD=your-app-password
```

### Step 3: Test Email Sending

Run this test script:
```python
from utils.email_sender import send_approval_email

# Test email
send_approval_email(
    recipient_email="test@example.com",
    org_name="Test NGO",
    temp_password="VAANI@1234"
)
```

## Email Templates

### Approval Email Includes:
- 🎉 Congratulations header
- Organization name
- Login credentials (email + temporary password)
- Security warning to change password
- Link to NGO dashboard
- Next steps checklist
- Contact information

### Rejection Email Includes:
- Polite notification
- Optional reason for rejection
- Encouragement to reapply
- Contact information

## How It Works

1. **Admin Action**: Admin approves/rejects NGO request via dashboard
2. **API Call**: `POST /api/admin/ngo-request/action`
3. **Email Trigger**: System automatically sends email
4. **Delivery**: NGO receives professional HTML email
5. **Logging**: Email status logged in console

## Development Mode

If `SENDER_PASSWORD` is not set, emails won't be sent but will be logged to console:
```
⚠️ Email not sent: SENDER_PASSWORD not configured
   Would send approval email to: ngo@example.com
   Organization: Example NGO
   Temp Password: VAANI@1234
```

This allows development without email configuration.

## Production Considerations

### Security:
- ✅ Use environment variables for credentials
- ✅ Never commit `.env` file to version control
- ✅ Use app passwords, not regular passwords
- ✅ Consider using dedicated email service (SendGrid, Mailgun, AWS SES)

### Reliability:
- Add retry logic for failed emails
- Queue emails for async sending
- Log all email attempts to database
- Monitor delivery rates

### Customization:
Edit `backend/utils/email_sender.py` to customize:
- Email templates (HTML/CSS)
- Subject lines
- Sender name
- Additional content

## Troubleshooting

### Email not sending?
1. Check `.env` file exists and has correct values
2. Verify SMTP credentials are correct
3. Check Gmail "Less secure app access" is disabled (use App Password instead)
4. Check spam folder for test emails
5. Review console logs for error messages

### Gmail blocking sign-in?
- Enable 2FA and use App Password (required)
- Check "Allow less secure apps" if using regular password (not recommended)

### Port issues?
- Port 587: TLS (recommended)
- Port 465: SSL (alternative)
- Port 25: Usually blocked by ISPs

## API Integration

The email functionality is automatically integrated with the admin approval endpoint:

```javascript
// Frontend example
fetch('/api/admin/ngo-request/action', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    request_id: 123,
    action: 'APPROVED'
  })
})
```

No additional frontend changes needed - emails are sent server-side.

## Future Enhancements

Potential improvements:
- [ ] Email delivery tracking
- [ ] Customizable templates via admin panel
- [ ] Scheduled email reminders
- [ ] Batch email sending
- [ ] Email analytics dashboard
- [ ] Multi-language support
