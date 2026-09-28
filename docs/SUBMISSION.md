# Lablab Submission Copy — Mini Challenge 2

Updated: 2026-09-28

## Recommended public title

ChispaVision: AMD Physical Asset Intelligence

Repository name remains `infralens-ocr-amd`; the public submission title is intentionally distinct from other projects named InfraLens.

## Long description

ChispaVision is an AMD ROCm vision pipeline built for Mini Challenge 2 that treats OCR as the first step of a useful physical-world workflow. The grader-facing core uses a deterministic Qwen2.5-VL-3B pipeline inside the mandated ROCm/PyTorch container, with a resident model service so repeated CLI calls do not reload the model. It is hardened for vehicle plates, mainland Chinese plates, multi-line road signs, numeric advisory plaques, blur, JPEG degradation, low light and perspective while keeping the required output strictly limited to text and confidence.

The same recognized text can optionally become an Asset Passport. A technician can photograph an NVR, camera, switch, access controller, router, inverter or equipment label and obtain structured candidate fields such as brand, model, serial number, MAC/IP information and electrical ratings. That product layer is isolated from the grader JSON.

The project also includes a separate HyperLoom optimization lane for the same multimodal workload on AMD hardware. HyperLoom candidates are accepted only when OCR correctness is preserved, turning the challenge into a real correctness-gated optimization workload rather than a one-off OCR demo.

Physical validation on an AMD Radeon AI PRO R9700 (`gfx1201`) passed the local acceptance corpus: 6/6 exact OCR fixtures, 50.340 s container startup, 1.687–4.072 s measured per-image latency, 17,829 MiB peak VRAM and a 24.673 GiB final image. Public-registry delivery remains a separate final gate and is not claimed complete until an anonymous pull is verified.

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
- HyperLoom research lane
- AMD Radeon AI PRO R9700

## One-line pitch

From difficult pixels to exact OCR, then from OCR to machine-readable physical assets on AMD.

## Demo sequence

1. Read a difficult challenge plate/sign.
2. Show exact OCR + confidence + AMD runtime evidence.
3. Scan a real infrastructure label and generate an Asset Passport.
4. Show the HyperLoom optimization lane and correctness gate.
5. Show baseline-vs-optimized performance only when comparative physical measurements exist.

## Claim boundary

Validated local R9700 measurements may be cited with the exact acceptance report. Do **not** claim public-registry availability, anonymous-pull validation, grader-private accuracy, or a HyperLoom speedup until those specific gates pass.
