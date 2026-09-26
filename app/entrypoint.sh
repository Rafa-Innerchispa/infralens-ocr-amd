#!/usr/bin/env bash
set -euo pipefail
export HF_HOME="${HF_HOME:-/models}"
export OCR_MODEL_ID="${OCR_MODEL_ID:-microsoft/trocr-base-printed}"
export OCR_BACKEND="${OCR_BACKEND:-trocr}"
export HF_HUB_OFFLINE="${HF_HUB_OFFLINE:-1}"
mkdir -p /app/input /app/output /models

python3 /app/server.py >/var/log/infralens-server.log 2>&1 &
server_pid=$!

for _ in $(seq 1 120); do
  if ! kill -0 "$server_pid" 2>/dev/null; then
    cat /var/log/infralens-server.log >&2 || true
    exit 1
  fi
  if python3 - <<'PY' >/dev/null 2>&1
import urllib.request
with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=1) as r:
    assert r.status == 200
PY
  then
    echo "InfraLens OCR ready"
    break
  fi
  sleep 3
done

if ! python3 - <<'PY' >/dev/null 2>&1
import urllib.request
with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=1) as r:
    assert r.status == 200
PY
then
  cat /var/log/infralens-server.log >&2 || true
  exit 1
fi

wait "$server_pid"
