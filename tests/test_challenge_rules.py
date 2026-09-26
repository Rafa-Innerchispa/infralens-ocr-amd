import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))
from challenge_rules import clean_text

class ChallengeRuleTests(unittest.TestCase):
    def test_drops_state_banner_from_plate(self):
        self.assertEqual(clean_text("CALIFORNIA 8ABC123"), "8ABC123")

    def test_drops_invented_unit_on_numeric_plaque(self):
        self.assertEqual(clean_text("35 MPH"), "35")

    def test_keeps_sign_words(self):
        self.assertEqual(clean_text("SPEED LIMIT 65"), "SPEED LIMIT 65")

    def test_chinese_serial_normalization(self):
        self.assertEqual(clean_text("京 A·12OI5"), "京A12015")

if __name__ == "__main__":
    unittest.main()
