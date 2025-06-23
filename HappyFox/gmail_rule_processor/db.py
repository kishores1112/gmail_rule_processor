import psycopg2
import os


def get_conn():
    """
    Establish a connection to the PostgreSQL database.

    Returns:
        psycopg2.connection: A connection object for interacting with the database.

    Environment Variables:
    - PGDATABASE: Name of the database.
    - PGUSER: Database user.
    - PGPASSWORD: Password for the database user.
    - PGHOST: Host where the database is running.
    - PGPORT: Port number for the database connection.
    """
    return psycopg2.connect(
        dbname=os.getenv("PGDATABASE", "mydatabase"),
        user=os.getenv("PGUSER", "myuser"),
        password=os.getenv("PGPASSWORD", "mypassword"),
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
    )


def init_db():
    """
    Initialize the database by creating the `emails` table if it does not already exist.

    Table Schema:
    - id: Auto-incrementing primary key.
    - gmail_id: Unique identifier for the email (from Gmail API).
    - sender: Email address of the sender.
    - recipient: Email address of the recipient.
    - subject: Subject of the email.
    - snippet: Snippet of the email content.
    - received: Date and time the email was received.

    Note:
    - Uses SERIAL for the primary key.
    - Ensures `gmail_id` is unique to avoid duplicate entries.
    """
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS emails (
            id SERIAL PRIMARY KEY,
            gmail_id TEXT UNIQUE,
            sender TEXT,
            recipient TEXT,
            subject TEXT,
            snippet TEXT,
            received TEXT
        )
    """
    )
    conn.commit()
    c.close()
    conn.close()


def insert_email(gmail_id, sender, recipient, subject, snippet, received):
    """
    Insert email metadata into the `emails` table.

    Parameters:
    - gmail_id (str): Unique identifier for the email (from Gmail API).
    - sender (str): Email address of the sender.
    - recipient (str): Email address of the recipient.
    - subject (str): Subject of the email.
    - snippet (str): Snippet of the email content.
    - received (str): Date and time the email was received.

    Note:
    - Ensures `gmail_id` is unique to avoid duplicate entries.
    - Uses ON CONFLICT to ignore duplicate entries based on `gmail_id`.
    """
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO emails (gmail_id, sender, recipient, subject, snippet, received)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (gmail_id) DO NOTHING
    """,
        (gmail_id, sender, recipient, subject, snippet, received),
    )
    conn.commit()
    c.close()
    conn.close()
