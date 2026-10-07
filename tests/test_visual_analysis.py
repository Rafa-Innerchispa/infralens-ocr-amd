from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from visual_analysis import normalize_analysis, prompt_for_task


class VisualAnalysisContractTests(unittest.TestCase):
    def test_general_prompt_is_fail_soft_and_structured(self):
        system, user = prompt_for_task("general")
        self.assertIn("Do not invent", system)
        self.assertIn('"summary"', user)
        self.assertIn('"visible_text"', user)

    def test_normalize_json_fence(self):
        raw = """```json
        {
          "summary": "Network switch label",
          "object_type": "switch",
          "visible_text": ["Cisco", "Catalyst 2960-X"],
          "identifiers": [{"kind": "model", "value": "2960-X"}],
          "observations": ["rack mounted"],
          "warnings": [],
          "confidence": 0.93
        }
        ```"""
        value = normalize_analysis(raw, "asset")
        self.assertEqual(value["object_type"], "switch")
        self.assertEqual(value["visible_text"][0], "Cisco")
        self.assertEqual(value["identifiers"][0]["kind"], "model")
        self.assertAlmostEqual(value["confidence"], 0.93)

    def test_unknown_task_falls_back_to_general(self):
        _system, user = prompt_for_task("anything")
        self.assertIn('"object_type"', user)

    def test_confidence_is_clamped(self):
        raw = '{"summary":"x","object_type":"unknown","visible_text":[],"identifiers":[],"observations":[],"warnings":[],"confidence":8}'
        value = normalize_analysis(raw, "general")
        self.assertEqual(value["confidence"], 1.0)


if __name__ == "__main__":
    unittest.main()
