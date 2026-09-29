#!/usr/bin/env python3
"""End-to-end validation for Challenge OCR, Asset Passport, and Batch Intake."""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "e2e"
OCR_PORT = int(os.environ.get("INFRALENS_OCR_PORT", "18765"))
UI_PORT = int(os.environ.get("INFRALENS_UI_PORT", "18501"))
OCR_URL = f"http://127.0.0.1:{OCR_PORT}"
UI_URL = f"http://127.0.0.1:{UI_PORT}"
HEALTH_TIMEOUT_S = int(os.environ.get("INFRALENS_HEALTH_TIMEOUT_S", "900"))


def wait_health() -> dict:
    deadline = time.time() + HEALTH_TIMEOUT_S
    last_err = ""
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{OCR_URL}/health", timeout=5) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
                if resp.status == 200 and payload.get("ok"):
                    return payload
        except Exception as exc:  # noqa: BLE001
            last_err = str(exc)
            time.sleep(5)
    raise TimeoutError(f"OCR backend not healthy after {HEALTH_TIMEOUT_S}s: {last_err}")


def call_ocr(path: Path) -> dict:
    data = path.read_bytes()
    req = urllib.request.Request(
        f"{OCR_URL}/ocr",
        data=data,
        headers={"Content-Type": "application/octet-stream"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def assert_challenge(result: dict) -> None:
    assert isinstance(result.get("text"), str)
    assert isinstance(result.get("confidence"), (int, float))
    assert result["confidence"] >= 0.0


def assert_asset_passport(result: dict) -> None:
    passport = result.get("asset_passport") or {}
    assert passport.get("asset_type") == "nvr"
    assert passport.get("brand") == "Hikvision"
    entities = passport.get("entities") or {}
    assert "E12345678" in (entities.get("serial_numbers") or [])
    assert "DS-7608NI-K2" in (entities.get("model_numbers") or [])


def assert_batch(results: list[dict]) -> None:
    assert len(results) == 2
    for item in results:
        assert "text" in item and "confidence" in item


def check_ui() -> None:
    with urllib.request.urlopen(f"{UI_URL}/_stcore/health", timeout=10) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Streamlit unhealthy: HTTP {resp.status}")


def main() -> int:
    if not FIXTURES.exists():
        import subprocess

        subprocess.run([sys.executable, str(ROOT / "scripts" / "generate_fixtures.py")], check=True)

    runtime = wait_health()
    print(json.dumps({"phase": "health", "runtime": runtime.get("runtime", {})}, indent=2))

    challenge = call_ocr(FIXTURES / "challenge_plate.png")
    assert_challenge(challenge)
    print(json.dumps({"phase": "challenge_ocr", "text": challenge["text"], "confidence": challenge["confidence"]}, indent=2))

    asset = call_ocr(FIXTURES / "asset_nvr_label.png")
    assert_challenge(asset)
    assert_asset_passport(asset)
    print(json.dumps({"phase": "asset_passport", "asset_type": asset["asset_passport"]["asset_type"]}, indent=2))

    batch = [
        call_ocr(FIXTURES / "challenge_plate.png"),
        call_ocr(FIXTURES / "batch_sign.png"),
    ]
    assert_batch(batch)
    print(json.dumps({"phase": "batch_intake", "files": 2, "rows": len(batch)}, indent=2))

    check_ui()
    print(json.dumps({"phase": "streamlit_ui", "url": UI_URL, "ok": True}, indent=2))
    print(json.dumps({"pass": True}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (urllib.error.URLError, TimeoutError, AssertionError) as exc:
        print(json.dumps({"pass": False, "error": str(exc)}, indent=2), file=sys.stderr)
        raise SystemExit(1) from exc
