from db import init_db, insert_email
from common import get_service


def fetch_and_store():
    """
    Fetch emails from the Gmail inbox and store them in the database.

    Steps:
    1. Initialize the database (creates tables if not already present).
    2. Authenticate with Gmail API using OAuth.
    3. Fetch up to 50 emails from the inbox.
    4. Extract relevant metadata (e.g., sender, recipient, subject, snippet, received date).
    5. Store the email details in the database.
    """
    # Initialize the database
    init_db()

    # Authenticate with Gmail API
    service = get_service()

    # Fetch up to 50 emails from the inbox
    results = (
        service.users()
        .messages()
        .list(userId="me", labelIds=["INBOX"], maxResults=50)
        .execute()
    )
    messages = results.get("messages", [])

    # Process each email
    for msg in messages:
        # Fetch detailed metadata for the email
        msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
        headers = {
            header["name"]: header["value"] for header in msg_data["payload"]["headers"]
        }

        # Extract relevant fields from the email headers
        sender = headers.get("From", "")
        recipient = headers.get("To", "")
        subject = headers.get("Subject", "")
        snippet = msg_data.get("snippet", "")
        received = headers.get("Date", "")

        # Insert email metadata into the database
        insert_email(msg["id"], sender, recipient, subject, snippet, received)

    print("Fetched and stored emails.")


if __name__ == "__main__":
    fetch_and_store()
