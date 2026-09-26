import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))
from asset_passport import build_asset_passport

class AssetPassportTests(unittest.TestCase):
    def test_extracts_infrastructure_identifiers(self):
        text = """Hikvision Network Video Recorder
MODEL: DS-7608NI-K2
S/N: E12345678
MAC: AA:BB:CC:DD:EE:FF
IP: 192.168.1.64
12V DC 2A"""
        p = build_asset_passport(text, 0.94, {"engine": "test"})
        self.assertEqual(p["brand"], "Hikvision")
        self.assertEqual(p["asset_type"], "nvr")
        self.assertIn("E12345678", p["entities"]["serial_numbers"])
        self.assertIn("DS-7608NI-K2", p["entities"]["model_numbers"])
        self.assertIn("AA:BB:CC:DD:EE:FF", p["entities"]["mac_addresses"])
        self.assertIn("192.168.1.64", p["entities"]["ipv4_addresses"])

if __name__ == "__main__":
    unittest.main()
