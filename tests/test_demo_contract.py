from __future__ import annotations

import ast
import unittest
from pathlib import Path


class DemoContractTests(unittest.TestCase):
    def test_demo_source_parses_and_exposes_capture_modes(self):
        source = (Path(__file__).resolve().parents[1] / "demo" / "app.py").read_text(encoding="utf-8")
        ast.parse(source)
        self.assertIn("st.camera_input", source)
        self.assertIn("Upload photo", source)
        self.assertIn("Batch upload", source)
        self.assertIn("General visual analysis", source)
        self.assertIn("Qwen2.5-VL-3B-Instruct", source)
        self.assertIn("Radeon AI PRO R9700", source)
        self.assertIn("No external vision API", source)


if __name__ == "__main__":
    unittest.main()
