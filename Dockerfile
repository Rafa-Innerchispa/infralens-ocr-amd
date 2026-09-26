# AMD AI Academy Mini Challenge 2 mandated base.
# The grader checks base-layer identity. Do not replace, flatten, or squash.
FROM rocm/pytorch:rocm10.0_ubuntu26.04_py3.14_pytorch_release_2.13.0

LABEL org.opencontainers.image.title="InfraLens OCR"
LABEL org.opencontainers.image.description="AMD ROCm OCR for physical infrastructure Asset Passports"
LABEL org.opencontainers.image.source="https://github.com/Rafa-Innerchispa/infralens-ocr-amd"

ENV DEBIAN_FRONTEND=noninteractive \
    HF_HOME=/models \
    OCR_MODEL_ID=microsoft/trocr-base-printed \
    OCR_BACKEND=trocr

WORKDIR /app
COPY app/requirements.txt /app/requirements.txt
RUN python3 -m pip install --no-cache-dir -r /app/requirements.txt

RUN python3 - <<'PY'
from transformers import AutoImageProcessor, RobertaTokenizer, VisionEncoderDecoderModel
model_id = "microsoft/trocr-base-printed"
cache = "/models"
AutoImageProcessor.from_pretrained(model_id, cache_dir=cache)
RobertaTokenizer.from_pretrained(model_id, cache_dir=cache, use_fast=False)
VisionEncoderDecoderModel.from_pretrained(model_id, cache_dir=cache)
print("prefetched", model_id)
PY

ENV HF_HUB_OFFLINE=1
COPY app/ /app/
RUN chmod +x /app/entrypoint.sh && mkdir -p /app/input /app/output /models

ENTRYPOINT ["bash", "/app/entrypoint.sh"]
