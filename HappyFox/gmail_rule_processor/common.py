import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the scope for Gmail API
GMAIL_SCOPE = ["https://www.googleapis.com/auth/gmail.modify"]


def get_service():
    """
    Authenticate and return the Gmail API service object.

    Returns:
        googleapiclient.discovery.Resource: Gmail API service object.
    """
    # Get the absolute path of the current script's directory
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct paths for credentials.json and token.json
    credentials_path = os.path.join(base_dir, "credentials.json")
    token_path = os.path.join(base_dir, "token.json")

    # Check if token.json exists
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, GMAIL_SCOPE)
    else:
        # If token.json doesn't exist, initiate OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_path,  # Use dynamically constructed path
            GMAIL_SCOPE,
        )
        creds = flow.run_local_server(port=0)
        # Save the credentials to token.json for future use
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)
