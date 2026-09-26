# Lablab Submission Copy - Mini Challenge 2

## Title

InfraLens OCR: Physical Assets to Data

## Long description

InfraLens OCR is an AMD ROCm vision pipeline that satisfies the Mini Challenge
2 OCR contract while extending it into something useful for real field
operations. The challenge core runs Qwen2.5-VL-3B on PyTorch/ROCm inside the
mandated AMD base image. The model is loaded and warmed once by a resident
service, while each grader invocation remains a thin CLI that writes exactly
the required text/confidence JSON.

The OCR engine is tuned for the public challenge rules: vehicle registration
plates, Chinese plates, multi-line road signs, numeric advisory plaques and
adverse images affected by blur, noise, low light or perspective. Bounded
test-time augmentation compares an original, normalized and enhanced view
without exceeding the per-image time budget. Deterministic cleanup removes
surrounding plate banners and avoids invented units.

I then reuse that OCR result in an optional InfraLens Asset Passport. A
technician can photograph an NVR, camera, network switch, access controller,
router, inverter or equipment label and obtain candidate brand, model, serial
number, MAC address, IP address and electrical ratings. The graded JSON remains
untouched; Asset Passport is emitted separately.

The goal is to turn OCR from a one-off demo into a reusable ingestion primitive
for inventory, maintenance and AI-assisted physical infrastructure.

## Suggested categories

- Computer Vision
- Developer Tools
- Productivity

## Technologies

- AMD ROCm
- PyTorch
- Qwen2.5-VL
- Hugging Face
- Docker
- Pillow

## One-line pitch

From difficult visual text to trusted OCR and machine-readable physical assets.
