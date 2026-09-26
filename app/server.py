"""Load OCR once and serve repeated images to the grading harness."""
from __future__ import annotations
import io
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from asset_passport import build_asset_passport
from engine import get_engine, runtime_metadata
from preprocess import enhance

ENGINE = None
RUNTIME = {}

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        return

    def _send(self, code: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"ok": True, "runtime": RUNTIME})
        else:
            self._send(404, {"error": "not_found"})

    def do_POST(self):
        if self.path != "/read":
            self._send(404, {"error": "not_found"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(size)
            image = enhance(Image.open(io.BytesIO(raw)).convert("RGB"))
            text, confidence, lines = ENGINE.read(image)
            self._send(200, {
                "text": text,
                "confidence": confidence,
                "lines": [
                    {"text": line.text, "confidence": line.confidence, "box": list(line.box)}
                    for line in lines
                ],
                "asset_passport": build_asset_passport(text, confidence, RUNTIME),
            })
        except Exception as exc:
            self._send(500, {"error": type(exc).__name__, "message": str(exc)})

if __name__ == "__main__":
    ENGINE = get_engine()
    RUNTIME = runtime_metadata(ENGINE)
    print("INFRALENS_READY " + json.dumps(RUNTIME, sort_keys=True), flush=True)
    ThreadingHTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
