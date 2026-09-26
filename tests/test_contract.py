import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except Exception:
    Image = None

class ContractTests(unittest.TestCase):
    @unittest.skipIf(Image is None, "Pillow not available")
    def test_stub_writes_exact_graded_contract(self):
        repo = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as td:
            image_path = Path(td) / "asset.png"
            outdir = Path(td) / "out"
            image = Image.new("RGB", (400, 120), "white")
            ImageDraw.Draw(image).text((20, 40), "INFRALENS TEST", fill="black")
            image.save(image_path)
            env = os.environ.copy()
            env["OCR_BACKEND"] = "stub"
            proc = subprocess.run(
                [sys.executable, str(repo / "app" / "app.py"),
                 "--input-image", str(image_path), "--output-dir", str(outdir)],
                env=env, text=True, capture_output=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads((outdir / "asset_output.json").read_text())
            self.assertEqual(set(payload), {"text", "confidence"})
            self.assertIsInstance(payload["text"], str)
            self.assertIsInstance(payload["confidence"], float)
            self.assertTrue((outdir / "asset_asset_passport.json").exists())

if __name__ == "__main__":
    unittest.main()
