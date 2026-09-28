"""Bake the open OCR model into the challenge image."""
from __future__ import annotations
import os
from pathlib import Path
from huggingface_hub import snapshot_download

model_id = os.environ.get("MODEL_ID", "Qwen/Qwen2.5-VL-3B-Instruct")
model_revision = os.environ.get("MODEL_REVISION", "66285546d2b821cf421d4f5eb2576359d3770cd3")
model_dir = Path(
    os.environ.get("MODEL_DIR", f"/models/{model_id.split('/')[-1]}")
)
model_dir.mkdir(parents=True, exist_ok=True)

snapshot_download(
    repo_id=model_id,
    revision=model_revision,
    local_dir=str(model_dir),
    ignore_patterns=["*.md", "*.gitattributes"],
)
print(f"MODEL_READY {model_id}@{model_revision} -> {model_dir}")
