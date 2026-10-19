from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINAL_IMAGE = "us-central1-docker.pkg.dev/innerops-agentic-platform/amd-academy-public/chispavision-mc2:final-512"


class PresentationDeploymentContractTests(unittest.TestCase):
    def test_presentation_backend_layers_on_frozen_artifact(self):
        dockerfile = (ROOT / "Dockerfile.presentation").read_text(encoding="utf-8")
        self.assertIn(f"FROM {FINAL_IMAGE}", dockerfile)
        self.assertIn("COPY app/visual_analysis.py", dockerfile)
        self.assertNotIn("download_model.py", dockerfile)

    def test_presentation_compose_keeps_private_backend(self):
        compose = (ROOT / "docker-compose.presentation.yml").read_text(encoding="utf-8")
        self.assertIn('container_name: infralens-track2-ocr', compose)
        self.assertIn('INFRALENS_ANALYZE_URL: "http://127.0.0.1:18765/analyze"', compose)
        self.assertIn('INFRALENS_UI_PORT: "18501"', compose)
        self.assertNotIn("ports:", compose)

    def test_demo_dockerfile_bundles_hero_asset(self):
        dockerfile = (ROOT / "demo" / "Dockerfile.ui").read_text(encoding="utf-8")
        self.assertIn("COPY hero_bg.b64", dockerfile)
        self.assertIn("streamlit run app.py", dockerfile)


if __name__ == "__main__":
    unittest.main()
