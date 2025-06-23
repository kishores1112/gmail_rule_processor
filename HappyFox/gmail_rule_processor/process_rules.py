import os
import json
import psycopg2
import psycopg2.extras
from db import get_conn
from common import get_service


def load_rules():
    """
    Load rules from the rules.json file.
    Returns:
        dict: A dictionary containing rules and actions.
    """
    try:
        # Get the relative path of the rules.json file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        rules_path = os.path.join(base_dir, "rules.json")

        # Load and return the rules
        with open(rules_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: rules.json file not found.")
        return {"rules": [], "actions": []}


def match_rule(email, condition):
    """
    Check if an email matches a specific condition.
    Supports string-based fields (e.g., From, Subject) and date-based fields (Received).

    Args:
        email (dict): Email metadata.
        condition (dict): Condition to evaluate.

    Returns:
        bool: True if the condition matches, False otherwise.
    """
    try:
        field = condition["field"].lower()
        value = condition["value"]
        predicate = condition["predicate"].lower()
        email_value = email.get(field, "")

        # Handle string-based rules (e.g., From, Subject)
        if predicate == "contains":
            return value.lower() in (email_value or "").lower()
        elif predicate == "does not contain":
            return value.lower() not in (email_value or "").lower()
        elif predicate == "equals":
            return (email_value or "").lower() == value.lower()
        elif predicate == "does not equal":
            return (email_value or "").lower() != value.lower()

        # Handle date-based rules (e.g., Received Date/Time)
        if field == "received date/time":
            from datetime import datetime, timedelta

            # Validate email_value before parsing
            if not email_value:
                print(f"Invalid date value for field '{field}': {email_value}")
                return False

            try:
                # Preprocess the date string to replace "GMT" with "+0000"
                email_value = email_value.replace("GMT", "+0000")

                # Parse the email date using the correct format
                email_date = datetime.strptime(email_value, "%a, %d %b %Y %H:%M:%S %z")

                # Calculate the comparison date
                days = int(value.split()[0])
                comparison_date = datetime.now(email_date.tzinfo) - timedelta(days=days)

                if predicate == "less than":
                    return email_date > comparison_date
                elif predicate == "greater than":
                    return email_date < comparison_date
            except ValueError as e:
                print(f"Error parsing date '{email_value}': {e}")
                return False

        return False
    except KeyError as e:
        print(f"Error in condition: {condition}, missing key: {e}")
        return False


def process_emails():
    """
    Process emails stored in the database based on rules defined in rules.json.
    Applies actions (e.g., mark as read/unread, move to label) to matching emails.
    """
    # Load rules and actions from rules.json
    ruleset = load_rules()

    # Connect to the database and fetch all emails
    conn = get_conn()
    c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        c.execute("SELECT * FROM emails")
        emails = c.fetchall()
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return

    # Authenticate with Gmail API
    service = get_service()

    # Process each email
    for email in emails:
        try:
            # Evaluate conditions for each rule
            for rule in ruleset.get("rules", []):
                conditions = rule.get("conditions", [])
                predicate = rule.get("predicate", "").lower()

                # Check if the email matches the conditions
                matches = [match_rule(email, condition) for condition in conditions]
                if (predicate == "all" and all(matches)) or (
                    predicate == "any" and any(matches)
                ):
                    # Apply actions to matching emails
                    for action in rule.get("actions", []):
                        if action["action"].lower() == "mark_read":
                            print(f"Marking {email['gmail_id']} as read")
                            service.users().messages().modify(
                                userId="me",
                                id=email["gmail_id"],
                                body={"removeLabelIds": ["UNREAD"]},
                            ).execute()
                        elif action["action"].lower() == "mark_unread":
                            print(f"Marking {email['gmail_id']} as unread")
                            service.users().messages().modify(
                                userId="me",
                                id=email["gmail_id"],
                                body={"addLabelIds": ["UNREAD"]},
                            ).execute()
                        elif action["action"].lower() == "move_message":
                            folder = action.get("folder", "")
                            if folder:
                                # Sanitize the folder name
                                sanitized_folder = "".join(
                                    char
                                    for char in folder
                                    if char.isalnum() or char in (" ", "-", "_")
                                ).strip()

                                # Check if the folder exists
                                labels = (
                                    service.users().labels().list(userId="me").execute()
                                )
                                label_map = {
                                    label["name"]: label["id"]
                                    for label in labels.get("labels", [])
                                }

                                if sanitized_folder not in label_map:
                                    print(f"Creating folder '{sanitized_folder}'")
                                    new_label = (
                                        service.users()
                                        .labels()
                                        .create(
                                            userId="me", body={"name": sanitized_folder}
                                        )
                                        .execute()
                                    )
                                    label_map[sanitized_folder] = new_label["id"]

                                print(
                                    f"Moving {email['gmail_id']} to folder '{sanitized_folder}'"
                                )
                                service.users().messages().modify(
                                    userId="me",
                                    id=email["gmail_id"],
                                    body={"addLabelIds": [label_map[sanitized_folder]]},
                                ).execute()
        except Exception as e:
            print(f"Error processing email {email['gmail_id']}: {e}")

    # Close the database connection
    c.close()
    conn.close()


if __name__ == "__main__":
    process_emails()
