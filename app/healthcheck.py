from __future__ import annotations
import os
import urllib.request

port = int(os.environ.get("OCR_PORT", "8765"))
with urllib.request.urlopen(
    f"http://127.0.0.1:{port}/health", timeout=3
) as response:
    if response.status != 200:
        raise SystemExit(1)
