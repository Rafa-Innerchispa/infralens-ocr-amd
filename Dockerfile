# AMD AI Academy Mini Challenge 2 mandated base.
# The grader checks base-layer identity. Do not replace, flatten, or squash.
FROM rocm/pytorch:rocm10.0_ubuntu26.04_py3.14_pytorch_release_2.13.0

ARG MODEL_ID=Qwen/Qwen2.5-VL-3B-Instruct
ARG MODEL_REVISION=66285546d2b821cf421d4f5eb2576359d3770cd3

LABEL org.opencontainers.image.title="InfraLens OCR"
LABEL org.opencontainers.image.description="AMD ROCm OCR with an Asset Passport extension"
LABEL org.opencontainers.image.source="https://github.com/Rafa-Innerchispa/infralens-ocr-amd"

ENV PYTHONUNBUFFERED=1 \
    HF_HUB_DISABLE_TELEMETRY=1 \
    MODEL_ID=\${MODEL_ID} \
    MODEL_REVISION=\${MODEL_REVISION} \
    MODEL_DIR=/models/Qwen2.5-VL-3B-Instruct \
    OCR_BACKEND=qwen \
    OCR_TTA_PASSES=3 \
    OCR_TIME_BUDGET_S=20 \
    OCR_MAX_NEW_TOKENS=256 \
    OCR_PORT=8765

WORKDIR /app

COPY app/requirements.txt /app/requirements.txt
RUN python3 -m pip install --no-cache-dir -r /app/requirements.txt

COPY app/download_model.py /app/download_model.py
RUN python3 /app/download_model.py

ENV HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1

COPY app/ /app/
RUN mkdir -p /app/input /app/output

HEALTHCHECK --interval=10s --timeout=5s --start-period=600s --retries=3 \
    CMD ["python3", "/app/healthcheck.py"]

ENTRYPOINT ["python3", "/app/server.py"]
