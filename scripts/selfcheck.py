from __future__ import annotations
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[1]
env = os.environ.copy()
env["OCR_BACKEND"] = "stub"

with tempfile.TemporaryDirectory() as td:
    src = Path(td) / "device.png"
    out = Path(td) / "output"
    image = Image.new("RGB", (500, 160), "white")
    ImageDraw.Draw(image).text((30, 65), "INFRALENS TEST", fill="black")
    image.save(src)
    proc = subprocess.run(
        [sys.executable, str(root / "app/app.py"),
         "--input-image", str(src), "--output-dir", str(out)],
        env=env, capture_output=True, text=True,
    )
    if proc.returncode:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        raise SystemExit(proc.returncode)
    graded = json.loads((out / "device_output.json").read_text())
    assert set(graded) == {"text", "confidence"}, graded
    assert graded["text"] == "INFRALENS TEST"
    assert (out / "device_asset_passport.json").exists()
    assert (out / "device_preview.jpg").exists()
    print(json.dumps({"pass": True, "graded": graded}, indent=2))
