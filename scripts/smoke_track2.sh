#!/usr/bin/env bash
# HTTP smoke checks for InfraLens Track 2 services.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OCR_PORT="${INFRALENS_OCR_PORT:-18765}"
UI_PORT="${INFRALENS_UI_PORT:-18501}"
OCR_BASE="http://127.0.0.1:${OCR_PORT}"
UI_BASE="http://127.0.0.1:${UI_PORT}"
FIXTURE="${ROOT}/fixtures/e2e/challenge_plate.png"

echo "== verify final-512 digest =="
bash "${ROOT}/scripts/verify_final512_digest.sh"

echo "== OCR /health =="
curl -sf "${OCR_BASE}/health" | python3 -m json.tool >/dev/null
echo "OK ${OCR_BASE}/health"

echo "== OCR /ocr (Challenge fixture) =="
if [[ ! -f "$FIXTURE" ]]; then
  python3 "${ROOT}/scripts/generate_fixtures.py"
fi
RESP="$(curl -sf -X POST "${OCR_BASE}/ocr" \
  -H "Content-Type: application/octet-stream" \
  --data-binary "@${FIXTURE}")"
python3 - <<'PY' "$RESP"
import json, sys
payload = json.loads(sys.argv[1])
assert "text" in payload and "confidence" in payload, payload
assert isinstance(payload["text"], str)
assert isinstance(payload["confidence"], (int, float))
print("OK /ocr text=%r confidence=%s" % (payload["text"][:80], payload["confidence"]))
PY

echo "== Streamlit UI =="
curl -sf "${UI_BASE}/_stcore/health" >/dev/null
echo "OK ${UI_BASE}/_stcore/health"

echo "All Track 2 smoke checks passed."
