import pandas as pd
import json
import os
import time
import base64
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CONFIG_FILE = "config.json"
EMAIL_DELAY = 10  # seconds between emails

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)

        last_reset = datetime.strptime(config['last_reset'], '%Y-%m-%d').date()

        if datetime.now().date() > last_reset:
            config['sent_today'] = 0
            config['last_reset'] = datetime.now().strftime('%Y-%m-%d')
            save_config(config)
    
        return config
    
    except (FileNotFoundError, json.JSONDecodeError):
        new_config = {
            'last_reset': datetime.now().strftime('%Y-%m-%d'),
            'sent_today': 0
        }
        save_config(new_config)
        return new_config

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def can_send_more(config):
    daily_limit = int(os.getenv('DAILY_LIMIT', 500))
    return config['sent_today'] < daily_limit

def get_gmail_service():
    """Authenticate and return Gmail API service"""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
    
    # If no valid credentials, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json',
                ['https://www.googleapis.com/auth/gmail.send']
            )
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)

def send_email(service, sender_email, recipient_email, subject, body):
    """Send email using Gmail API"""
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    html = f"""
    <div style="font-family: 'Google Sans',Roboto,RobotoDraft,Helvetica,Arial,sans-serif; font-size: 14px; color: #202124; line-height: 1.5;">
        {body}
        <div style="margin-top: 20px; font-size: 12px; color: #5f6368;">
            <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 15px 0;">
        </div>
    </div>
    """

    msg.attach(MIMEText(html, 'html'))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    
    try:
        service.users().messages().send(
            userId="me",
            body={'raw': raw}
        ).execute()
        return True
    except Exception as e:
        print(f"Gmail API error: {e}")
        return False

def send_bulk_emails(excel_file, subject, email_template):
    config = load_config()

    if not can_send_more(config):
        print("Daily email limit reached. Try again tomorrow")
        return
    
    try:
        df = pd.read_excel(excel_file, engine='openpyxl')
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return
    
    sender_email = os.getenv('GMAIL_ADDRESS')
    
    try:
        service = get_gmail_service()
        print("Successfully authenticated with Gmail API")
    except Exception as e:
        print(f"Failed to authenticate with Gmail: {e}")
        return
    
    success_count = 0
    failure_count = 0

    for _, row in df.iterrows():
        if not can_send_more(config):
            print(f"Stopping: Reached daily limit of {os.getenv('DAILY_LIMIT')} emails")
            break

        try:
            personalised_body = email_template.format(**row.to_dict())

            if send_email(service, sender_email, row['email'], subject, personalised_body):
                config['sent_today'] += 1
                success_count += 1
                save_config(config)

                print(f"Sent email to {row['name']} ({row['email']})")
                print(f"Emails sent today: {config['sent_today']}/{os.getenv('DAILY_LIMIT')}")

                if _ < len(df) - 1:
                    print(f"Waiting {EMAIL_DELAY} seconds before next email...")
                    time.sleep(EMAIL_DELAY)
            else:
                failure_count += 1

        except Exception as e:
            print(f"Failed to send email to {row.get('name', 'unknown')}: {str(e)}")
            failure_count += 1

    print(f"\nSummary - Success: {success_count}, Failures: {failure_count}")
    print(f"Total emails sent today: {config['sent_today']}/{os.getenv('DAILY_LIMIT')}")

if __name__ == "__main__":
    # Config
    EXCEL_FILE = "recipients.xlsx"
    EMAIL_SUBJECT = ""
    EMAIL_TEMPLATE = """
    <p>Hey {name},</p>
    <p></p>
    """

    send_bulk_emails(EXCEL_FILE, EMAIL_SUBJECT, EMAIL_TEMPLATE)