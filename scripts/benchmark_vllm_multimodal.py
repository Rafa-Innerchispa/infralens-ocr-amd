#!/usr/bin/env python3
"""Benchmark a Qwen2.5-VL OpenAI-compatible vLLM endpoint with InfraLens OCR cases.

This is an optional HyperLoom research lane. It does not replace the AMD grader
container contract.
"""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import statistics
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / "app"))
from challenge_rules import USER_PROMPT, clean_text

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}

def data_url(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"

def request_ocr(base_url: str, model: str, image: Path, timeout: float) -> tuple[str, float]:
    payload = {
        "model": model,
        "temperature": 0,
        "max_tokens": 64,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": data_url(image)}},
                {"type": "text", "text": USER_PROMPT},
            ],
        }],
    }
    req = urllib.request.Request(
        base_url.rstrip("/") + "/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    with urllib.request.urlopen(req, timeout=timeout) as response:
        result = json.loads(response.read().decode("utf-8"))
    latency = time.perf_counter() - started
    raw = result["choices"][0]["message"]["content"]
    return clean_text(str(raw)), latency

def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    pos = (len(ordered) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(ordered) - 1)
    frac = pos - lo
    return ordered[lo] * (1 - frac) + ordered[hi] * frac

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--base-url", default="http://127.0.0.1:18031")
    p.add_argument("--model", default="Qwen/Qwen2.5-VL-3B-Instruct")
    p.add_argument("--images", required=True, help="Directory containing OCR images")
    p.add_argument("--expected", default="", help="Optional JSON mapping filename -> exact expected text")
    p.add_argument("--repeats", type=int, default=3)
    p.add_argument("--timeout", type=float, default=30)
    p.add_argument("--output", default="hyperloom_infralens_benchmark.json")
    args = p.parse_args()

    images_dir = Path(args.images)
    images = sorted(x for x in images_dir.iterdir() if x.suffix.lower() in IMAGE_EXTS)
    if not images:
        raise SystemExit("no images found")

    expected = {}
    if args.expected:
        expected = json.loads(Path(args.expected).read_text(encoding="utf-8"))

    rows = []
    latencies = []
    exact_total = 0
    exact_possible = 0

    for image in images:
        for repeat in range(args.repeats):
            text, latency = request_ocr(args.base_url, args.model, image, args.timeout)
            latencies.append(latency)
            wanted = expected.get(image.name)
            exact = None
            if wanted is not None:
                exact_possible += 1
                exact = text == clean_text(str(wanted))
                exact_total += int(exact)
            rows.append({
                "image": image.name,
                "repeat": repeat + 1,
                "text": text,
                "expected": wanted,
                "exact": exact,
                "latency_s": round(latency, 6),
            })

    summary = {
        "schema": "infralens.hyperloom_benchmark.v1",
        "base_url": args.base_url,
        "model": args.model,
        "images": len(images),
        "requests": len(rows),
        "repeats": args.repeats,
        "cold_first_request_s": round(latencies[0], 6) if latencies else None,
        "median_latency_s": round(statistics.median(latencies), 6) if latencies else None,
        "p50_latency_s": round(percentile(latencies, 0.50), 6) if latencies else None,
        "p95_latency_s": round(percentile(latencies, 0.95), 6) if latencies else None,
        "exact_matches": exact_total if exact_possible else None,
        "exact_total": exact_possible if exact_possible else None,
        "exact_rate": round(exact_total / exact_possible, 6) if exact_possible else None,
        "results": rows,
    }
    Path(args.output).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items() if k != "results"}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
