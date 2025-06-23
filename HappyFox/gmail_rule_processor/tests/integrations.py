import unittest
from unittest.mock import patch, MagicMock
from fetch_emails import fetch_and_store
from process_rules import process_emails
from db import init_db, insert_email, get_conn


class TestIntegration(unittest.TestCase):
    @patch("process_rules.get_service")
    @patch("process_rules.get_conn")
    def test_process_emails(self, mock_get_conn, mock_get_service):
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {
                "gmail_id": "123",
                "subject": "Invoice for your purchase",
                "from": "boss@example.com",
            },
            {
                "gmail_id": "456",
                "subject": "Meeting agenda",
                "from": "employee@example.com",
            },
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        # Mock Gmail API service
        mock_service = MagicMock()
        mock_service.users().messages().modify.return_value = MagicMock()
        mock_service.users().labels().list.return_value.execute.return_value = {
            "labels": [{"name": "Important", "id": "label_important"}]
        }
        mock_service.users().labels().create.return_value.execute.return_value = {
            "id": "label_happyfox"
        }
        mock_get_service.return_value = mock_service

        # Run the process_emails function
        process_emails()

        # Assert database interaction
        mock_cursor.execute.assert_called_once_with("SELECT * FROM emails")
        mock_cursor.fetchall.assert_called_once()

        # Assert Gmail API interaction for marking emails as read
        mock_service.users().messages().modify.assert_any_call(
            userId="me",
            id="123",
            body={"removeLabelIds": ["UNREAD"]},
        )

        # Assert Gmail API interaction for moving emails to a folder
        mock_service.users().messages().modify.assert_any_call(
            userId="me",
            id="456",
            body={"addLabelIds": ["label_happyfox"]},
        )


if __name__ == "__main__":
    unittest.main()
