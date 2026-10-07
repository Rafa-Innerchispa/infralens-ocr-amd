# Judge Presentation Deployment

This deployment is presentation-only. It must never rebuild or overwrite the immutable MC2 grader artifact.

## Immutable grader artifact

`us-central1-docker.pkg.dev/innerops-agentic-platform/amd-academy-public/chispavision-mc2:final-512`

Digest:

`sha256:dbfcaf89fc2d47823406c1ceeefef464a98a7e4328226511ab1625c3d721868f`

## Presentation architecture

```text
browser camera / upload
        |
        v
https://infralens.creatorcore.ai/
        |
        v
Streamlit :18501
        |
        +--> /ocr
        |
        +--> /analyze
                 |
                 v
Qwen2.5-VL-3B-Instruct
Radeon AI PRO R9700 / ROCm
```

The presentation backend is a thin overlay image built FROM the immutable `final-512` artifact. It reuses the exact model weights already present in the validated image, so only one Qwen2.5-VL instance needs to be resident during the public demo.

## Capture modes

- Browser camera: webcam, USB camera or mobile camera exposed by the user's browser.
- Single photo upload.
- Batch photo upload.

The browser owns camera capture and permission. The AMD host receives the captured image only after the user takes the photo.

## Analysis modes

- Challenge OCR: existing graded OCR path.
- Identify an asset: structured visual equipment analysis + Asset Passport.
- General visual analysis: evidence-first structured description for ordinary visible objects.
- Visual field inspection: non-authoritative visible observations/review items.

## Model transparency

- Pixel/vision model: `Qwen/Qwen2.5-VL-3B-Instruct`.
- GPU: physical AMD Radeon AI PRO R9700 on node 1.5.
- Acceleration: AMD ROCm/HIP.
- Resident text reasoning service also present on node 1.5: `QuantTrio/Qwen3-Coder-30B-A3B-Instruct-AWQ`.
- Qwen3-Coder is not claimed to see pixels. The current visual analysis endpoint uses Qwen2.5-VL.

## Deployment invariant

Before switching containers, record:
- current `infralens-track2-ocr` container ID and image ID;
- current `infralens-track2-ui` container ID and image ID;
- public HTTP status.

Build the presentation images first. Only after successful builds:
1. stop/remove the current UI and OCR containers;
2. start `docker-compose.presentation.yml`;
3. wait for `/health`;
4. validate `/ocr` and `/analyze`;
5. validate public HTTPS;
6. roll back to the previous containers/images on any failure.

The registry artifact `final-512` is never changed.
