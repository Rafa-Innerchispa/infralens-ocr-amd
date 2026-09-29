"""Track 2 deployment helpers and optional live smoke tests."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIGEST = "sha256:dbfcaf89fc2d47823406c1ceeefef464a98a7e4328226511ab1625c3d721868f"
FINAL512 = (
    "us-central1-docker.pkg.dev/innerops-agentic-platform/amd-academy-public/"
    "chispavision-mc2:final-512"
)


class Track2DeployTests(unittest.TestCase):
    def test_compose_file_references_final512_without_build(self) -> None:
        compose = (ROOT / "docker-compose.track2.yml").read_text()
        self.assertIn("chispavision-mc2:final-512", compose)
        self.assertNotIn("build:", compose.split("ocr-backend:")[1].split("streamlit-ui:")[0])

    def test_verify_digest_script_passes_when_image_present(self) -> None:
        proc = subprocess.run(
            ["bash", str(ROOT / "scripts" / "verify_final512_digest.sh")],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0 and "image not present" in proc.stderr:
            self.skipTest("final-512 image not available on this host")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn(EXPECTED_DIGEST, proc.stdout)

    def test_generate_fixtures(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "generate_fixtures.py")],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        for name in ("challenge_plate.png", "asset_nvr_label.png", "batch_sign.png"):
            self.assertTrue((ROOT / "fixtures" / "e2e" / name).exists(), name)


class Track2LiveSmokeTests(unittest.TestCase):
    @classmethod
    def _backend_up(cls) -> bool:
        port = os.environ.get("INFRALENS_OCR_PORT", "18765")
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=3) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
                return resp.status == 200 and payload.get("ok") is True
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            return False

    @unittest.skipUnless(
        os.environ.get("INFRALENS_LIVE_SMOKE") == "1",
        "set INFRALENS_LIVE_SMOKE=1 to run against a live backend",
    )
    def test_live_smoke_script(self) -> None:
        if not self._backend_up():
            self.skipTest("Track 2 OCR backend is not running")
        proc = subprocess.run(
            ["bash", str(ROOT / "scripts" / "smoke_track2.sh")],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
