from google_auth_oauthlib.flow import InstalledAppFlow

# OAuth 2.0 Scopes (only what you need)
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def generate_oauth_tokens():
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json',  # The file you downloaded
        scopes=SCOPES
    )
    
    # This will open your browser for authentication
    creds = flow.run_local_server(port=0)
    
    # Save tokens for future use
    with open('token.json', 'w') as token_file:
        token_file.write(creds.to_json())
    print("OAuth tokens successfully saved to token.json")

if __name__ == '__main__':
    generate_oauth_tokens()