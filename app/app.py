"""AMD Mini Challenge 2 CLI contract plus optional InfraLens artifacts."""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from asset_passport import build_asset_passport
from ocr_engine import get_engine, runtime_metadata

PORT = int(os.environ.get("OCR_PORT", "8765"))

def _daemon_health(timeout_s: float = 8.0) -> bool:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(
                f"http://127.0.0.1:{PORT}/health", timeout=1
            ) as response:
                if response.status == 200:
                    return True
        except Exception:
            time.sleep(0.25)
    return False

def via_daemon(path: str) -> dict:
    if not _daemon_health():
        raise RuntimeError("resident OCR service is not ready")
    request = urllib.request.Request(
        f"http://127.0.0.1:{PORT}/ocr",
        data=Path(path).read_bytes(),
        headers={"Content-Type": "application/octet-stream"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=25) as response:
        return json.loads(response.read().decode("utf-8"))

def local_read(path: str) -> dict:
    with Image.open(path) as source:
        image = source.convert("RGB")
    engine = get_engine()
    text, confidence, info = engine.read(image)
    runtime = runtime_metadata(engine)
    return {
        "text": text,
        "confidence": confidence,
        "info": info,
        "asset_passport": build_asset_passport(
            text, confidence, runtime
        ),
    }

def write_preview(source_path: str, output: Path, text: str) -> None:
    try:
        with Image.open(source_path) as source:
            image = source.convert("RGB")
        draw = ImageDraw.Draw(image)
        label = text[:100]
        if label:
            draw.rectangle((0, 0, image.width, 28), fill="black")
            draw.text((8, 8), label, fill="white")
        image.save(output, quality=92)
    except Exception:
        pass

def main() -> int:
    parser = argparse.ArgumentParser(description="InfraLens OCR on AMD ROCm")
    parser.add_argument("--input-image", required=True)
    parser.add_argument(
        "--output-dir",
        default=os.environ.get("APP_OUTPUT_DIR", "/app/output"),
    )
    args = parser.parse_args()

    source = Path(args.input_image)
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    stem = source.stem

    result: dict
    try:
        if os.environ.get("OCR_BACKEND", "").lower() == "stub":
            result = local_read(str(source))
        else:
            result = via_daemon(str(source))
    except Exception as exc:
        print(
            f"InfraLens warning: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        result = {
            "text": "",
            "confidence": 0.0,
            "info": {"error": type(exc).__name__},
        }

    required = {
        "text": str(result.get("text", "")),
        "confidence": float(result.get("confidence", 0.0)),
    }
    required["confidence"] = max(
        0.0, min(1.0, required["confidence"])
    )

    graded = outdir / f"{stem}_output.json"
    graded.write_text(
        json.dumps(required, ensure_ascii=False),
        encoding="utf-8",
    )

    passport = result.get("asset_passport")
    if isinstance(passport, dict):
        (outdir / f"{stem}_asset_passport.json").write_text(
            json.dumps(
                passport,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    write_preview(
        str(source),
        outdir / f"{stem}_preview.jpg",
        required["text"],
    )
    print(json.dumps(required, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
