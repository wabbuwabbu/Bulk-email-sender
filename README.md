# Bulk Email Sender Documentation

A future-proof bulk email tool for Gmail that replaces SMTP passwords with OAuth 2.0, supports HTML templates, and enforces rate limits.

## Table of Contents
- [Overview](#overview)
- [Setup Guide](#setup-guide)
  - [Personal Gmail](#personal-gmail)
  - [Google Workspace](#google-workspace)
  - [OAuth 2.0 Configuration](#oauth-20-configuration)
  - [Script Installation](#script-installation)
- [Usage Guide](#usage-guide)
- [Troubleshooting](#troubleshooting)
- [Security & Best Practices](#security--best-practices)
- [FAQs](#faqs)

## Overview
This tool enables automated bulk email sending through Gmail using OAuth 2.0 for secure authentication.

**Key Features**:
- ✅ Send personalized HTML emails from Excel lists
- ✅ OAuth 2.0 security (no password storage)
- ✅ Rate limiting to comply with Gmail quotas
- ✅ Gmail-like email formatting

## Setup Guide

### Personal Gmail
**Enable Gmail API**:
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project and enable the Gmail API.
3. Configure the OAuth Consent Screen:
   - Set **User Type**: External
   - Add scopes:
     - `https://www.googleapis.com/auth/gmail.send`
     - `https://www.googleapis.com/auth/gmail.compose`
   - Add your email as a Test User.
4. Create OAuth Credentials:
   - Go to **Credentials** → **OAuth Client ID** → Select **Desktop App**.
   - Download the `credentials.json` file.

### Google Workspace
Requires admin access:
- **Domain-wide Delegation (Recommended)**:
  1. In Admin Console, go to **Security** → **API Controls**.
  2. Add OAuth scopes matching those in your app.
- **Service Account (For server-to-server)**:
  1. Create a service account in Google Cloud Console.
  2. Download the JSON key.

### OAuth 2.0 Configuration
**First-Time Authentication**:
Run the following Python code to authenticate and generate `token.json`:

```python
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json',
    scopes=SCOPES
)
creds = flow.run_local_server(port=0)  # Follow browser prompts

# Save tokens
with open('token.json', 'w') as token:
    token.write(creds.to_json())
```
Alternatively, run: `OAuth setup.py`

This generates `token.json` for future use.

### Script Installation
**Requirements**:
```bash
pip install pandas google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dotenv
```

**File Structure**:
```
email_sender/
├── credentials.json   # OAuth client config
├── token.json         # Auto-generated tokens
├── recipients.xlsx    # Email list (Name, Email columns)
├── .env               # Config (DAILY_LIMIT=500)
└── sender.py          # Main script
```

## Usage Guide
1. **Prepare Excel File** (`recipients.xlsx`):
   ```
   Name | Email            | Company
   John | john@example.com | Acme Inc
   ```

2. **Customize Email Template**:
   Edit the template in `main.py`:

   ```python
   HTML_TEMPLATE = """
   <p>Hi {name},</p>
   <p>This is a test email sent to {company}.</p>
   <a href="https://example.com">Click Here</a>
   """
   ```

3. **Run Bulk Sender**:
   ```bash
   python main.py
   ```
   Emails are sent with a 10-second delay between each to avoid rate limits.

## Troubleshooting
| **Error**                  | **Solution**                                      |
|----------------------------|--------------------------------------------------|
| 403 Quota Exceeded         | Wait 24 hours or request a quota increase.       |
| Invalid Grant              | Delete `token.json` and re-authenticate.         |
| SMTP Not Enabled           | Enable Gmail API in Google Cloud Console.        |

## Security & Best Practices
🔒 **Do NOT share**:
- `credentials.json`
- `token.json`

⚠️ **Recommendations**:
- Use Google Workspace for sending >500 emails/day.
- Store secrets in `.env`.
- Monitor sent counts in `config.json`.

## FAQs
**Q: Can I send attachments?**  
A: Yes! Modify the `send_email()` function to use `MIMEMultipart()` with `MIMEBase` attachments.

**Q: How to increase daily limits?**  
A: Upgrade to Google Workspace (supports up to 2,000 emails/day).

**Q: Why OAuth instead of SMTP?**  
A: Google is deprecating password-based SMTP in 2025.