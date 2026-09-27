import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))
from challenge_rules import clean_text
from ocr_engine import generation_complete

class ChallengeRuleTests(unittest.TestCase):
    def test_drops_state_banner_from_plate(self):
        self.assertEqual(clean_text("CALIFORNIA 8ABC123"), "8ABC123")

    def test_drops_invented_unit_on_numeric_plaque(self):
        self.assertEqual(clean_text("35 MPH"), "35")

    def test_keeps_sign_words(self):
        self.assertEqual(clean_text("SPEED LIMIT 65"), "SPEED LIMIT 65")

    def test_chinese_serial_normalization(self):
        self.assertEqual(clean_text("京 A·12OI5"), "京A12015")

    def test_generation_complete_with_eos(self):
        self.assertTrue(generation_complete([10, 11, 2], 2, 3))

    def test_generation_complete_under_budget_without_eos(self):
        self.assertTrue(generation_complete([10, 11], 2, 3))

    def test_generation_fails_closed_at_budget_without_eos(self):
        self.assertFalse(generation_complete([10, 11, 12], 2, 3))

if __name__ == "__main__":
    unittest.main()
