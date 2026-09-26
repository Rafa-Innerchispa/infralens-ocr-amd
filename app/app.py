"""Exact AMD Mini Challenge 2 CLI plus optional InfraLens artifacts."""
from __future__ import annotations
import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path
from PIL import ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from asset_passport import build_asset_passport
from engine import get_engine, runtime_metadata
from preprocess import load_image

def via_daemon(path: str) -> dict:
    request = urllib.request.Request(
        "http://127.0.0.1:8000/read",
        data=Path(path).read_bytes(),
        headers={"Content-Type": "application/octet-stream"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=25) as response:
        return json.loads(response.read().decode("utf-8"))

def local_read(path: str) -> dict:
    image = load_image(path)
    engine = get_engine()
    text, confidence, lines = engine.read(image)
    runtime = runtime_metadata(engine)
    return {
        "text": text,
        "confidence": confidence,
        "lines": [
            {"text": line.text, "confidence": line.confidence, "box": list(line.box)}
            for line in lines
        ],
        "asset_passport": build_asset_passport(text, confidence, runtime),
    }

def write_annotation(src: str, output: Path, lines: list[dict]) -> None:
    try:
        image = load_image(src)
        draw = ImageDraw.Draw(image)
        for line in lines:
            box = tuple(int(x) for x in line.get("box", []))
            if len(box) == 4:
                draw.rectangle(box, width=3)
                draw.text((box[0] + 3, max(0, box[1] - 14)), str(line.get("text", ""))[:48])
        image.save(output, quality=92)
    except Exception:
        pass

def main() -> int:
    parser = argparse.ArgumentParser(description="InfraLens OCR on AMD ROCm")
    parser.add_argument("--input-image", required=True)
    parser.add_argument("--output-dir", default=os.environ.get("APP_OUTPUT_DIR", "/app/output"))
    args = parser.parse_args()

    source = Path(args.input_image)
    if not source.is_file():
        parser.error(f"input image does not exist: {source}")

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    stem = source.stem

    try:
        result = via_daemon(str(source))
    except Exception:
        result = local_read(str(source))

    required = {
        "text": str(result.get("text", "")),
        "confidence": float(result.get("confidence", 0.0)),
    }
    required["confidence"] = max(0.0, min(1.0, required["confidence"]))

    (outdir / f"{stem}_output.json").write_text(
        json.dumps(required, ensure_ascii=False), encoding="utf-8"
    )

    passport = result.get("asset_passport")
    if isinstance(passport, dict):
        (outdir / f"{stem}_asset_passport.json").write_text(
            json.dumps(passport, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    write_annotation(str(source), outdir / f"{stem}_annotated.jpg", result.get("lines") or [])

    print(json.dumps(required, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
