import unittest
from process_rules import match_rule, load_rules
from unittest.mock import patch


class TestProcessRules(unittest.TestCase):
    def test_match_rule_contains(self):
        email = {"subject": "Invoice for your purchase"}
        rule = {"field": "Subject", "predicate": "Contains", "value": "Invoice"}
        self.assertTrue(match_rule(email, rule))

    def test_match_rule_equals(self):
        email = {"from": "boss@example.com"}
        rule = {"field": "From", "predicate": "Equals", "value": "boss@example.com"}
        self.assertTrue(match_rule(email, rule))

    def test_match_rule_does_not_contain(self):
        email = {"subject": "Meeting agenda"}
        rule = {"field": "Subject", "predicate": "Does Not Contain", "value": "Invoice"}
        self.assertTrue(match_rule(email, rule))

    def test_match_rule_does_not_equal(self):
        email = {"from": "employee@example.com"}
        rule = {
            "field": "From",
            "predicate": "Does Not Equal",
            "value": "boss@example.com",
        }
        self.assertTrue(match_rule(email, rule))

    def test_match_rule_less_than_date(self):
        email = {"received date/time": "Sun, 22 Jun 2025 12:56:09 +0000"}
        rule = {
            "field": "Received Date/Time",
            "predicate": "Less than",
            "value": "30 days",
        }
        self.assertTrue(match_rule(email, rule))

    def test_match_rule_greater_than_date(self):
        email = {"received date/time": "Sun, 22 Jun 2025 12:56:09 +0000"}
        rule = {
            "field": "Received Date/Time",
            "predicate": "Greater than",
            "value": "1 days",
        }
        self.assertFalse(match_rule(email, rule))

    @patch("process_rules.os.path.join")
    @patch("process_rules.open")
    def test_load_rules(self, mock_open, mock_path_join):
        mock_path_join.return_value = "rules.json"
        mock_open.return_value.__enter__.return_value.read.return_value = '{"rules": [{"field": "Subject", "predicate": "Contains", "value": "Invoice"}], "actions": []}'
        rules = load_rules()
        self.assertEqual(
            rules,
            {
                "rules": [
                    {"field": "Subject", "predicate": "Contains", "value": "Invoice"}
                ],
                "actions": [],
            },
        )


if __name__ == "__main__":
    unittest.main()
