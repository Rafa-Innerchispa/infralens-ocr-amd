"""Resident OCR service: model is loaded and warmed once at container startup."""
from __future__ import annotations

import io
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from asset_passport import build_asset_passport
from ocr_engine import get_engine, runtime_metadata

ENGINE = None
RUNTIME = {}
PORT = int(os.environ.get("OCR_PORT", "8765"))

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        return

    def send_json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self.send_json(200, {
                "ok": True,
                "runtime": RUNTIME,
                "capabilities": ["challenge_ocr", "visual_analysis", "asset_passport"],
            })
        else:
            self.send_json(404, {"error": "not_found"})

    def do_POST(self):
        if self.path not in {"/ocr", "/analyze"}:
            self.send_json(404, {"error": "not_found"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(size)
            image = Image.open(io.BytesIO(raw)).convert("RGB")

            if self.path == "/ocr":
                text, confidence, info = ENGINE.read(image)
                self.send_json(200, {
                    "text": text,
                    "confidence": confidence,
                    "info": info,
                    "asset_passport": build_asset_passport(
                        text, confidence, RUNTIME
                    ),
                    "runtime": RUNTIME,
                })
                return

            task = self.headers.get("X-InfraLens-Task", "general")
            analysis, info = ENGINE.analyze(image, task=task)
            visible_text = "\n".join(analysis.get("visible_text") or [])
            passport = build_asset_passport(
                visible_text,
                float(analysis.get("confidence", 0.0)),
                RUNTIME,
            )
            if analysis.get("object_type") and analysis.get("object_type") != "unknown":
                passport["asset_type"] = analysis["object_type"]
            if analysis.get("brand"):
                passport["brand"] = analysis["brand"]
            self.send_json(200, {
                "analysis": analysis,
                "info": info,
                "asset_passport": passport,
                "runtime": RUNTIME,
            })
        except Exception as exc:
            self.send_json(500, {
                "error": type(exc).__name__,
                "message": str(exc),
            })

if __name__ == "__main__":
    ENGINE = get_engine()
    ENGINE.warmup()
    RUNTIME = runtime_metadata(ENGINE)
    print(
        "INFRALENS_READY " + json.dumps(RUNTIME, sort_keys=True),
        flush=True,
    )
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()