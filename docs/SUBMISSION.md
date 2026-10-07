# Lablab Submission Copy — Mini Challenge 2

Updated: 2026-10-07

## Recommended public title

ChispaVision: AMD Physical Asset Intelligence

Repository name remains `infralens-ocr-amd`; the public submission title is intentionally distinct from other projects named InfraLens.

## Public judge demo

**https://infralens.creatorcore.ai/**

The public demo is a presentation layer only. The immutable grader artifact remains separate.

## Long description

ChispaVision is an AMD ROCm vision pipeline built for Mini Challenge 2 that treats OCR as the first step of a useful physical-world workflow.

The grader-facing core uses a deterministic Qwen2.5-VL-3B pipeline inside the mandated ROCm/PyTorch container, with a resident model service so repeated CLI calls do not reload the model. It is hardened for vehicle plates, multi-line road signs, numeric advisory plaques, blur, JPEG degradation, low light and perspective while keeping the required grader output strictly limited to text and confidence.

The presentation layer turns that challenge capability into **physical asset intelligence**:

```text
real-world photo
  -> local AMD ROCm vision
  -> exact OCR
  -> infrastructure understanding
  -> structured Asset Passport
  -> inventory / FieldOps / automation
```

A technician can photograph an NVR, camera, switch, access controller, router, inverter or equipment label and obtain structured candidate fields such as device type, brand, serial number, MAC/IP information and electrical ratings. Batch Intake applies the same workflow to multiple field photos to produce an inventory preview. This product layer is isolated from the grader JSON.

The public judge experience is intentionally simple: one local engine, three workflows.

1. **Challenge OCR** proves the official OCR requirement.
2. **Asset Passport** demonstrates how recognized text becomes machine-readable infrastructure.
3. **Batch Intake** demonstrates how repeated field photos become candidate inventory records.

No uploaded image is sent to an external vision API by the demo. The UI talks to the resident local InfraLens OCR service on the AMD host.

The project also includes a separate HyperLoom optimization lane for the same multimodal workload on AMD hardware. HyperLoom candidates are accepted only when OCR correctness is preserved, turning the challenge into a real correctness-gated optimization workload rather than a one-off OCR demo.

The final hardened artifact was validated on an AMD Radeon AI PRO R9700 (`gfx1201`), published to Google Artifact Registry, pulled anonymously with an empty Docker configuration, and then run again on the physical R9700. The public 512-token artifact reproduced exact OCR for `8ABC123`, `ROAD WORK AHEAD`, and `35` with measured warm latencies of 1.666 s, 1.721 s, and 1.307 s respectively.

## Verified public image

`us-central1-docker.pkg.dev/innerops-agentic-platform/amd-academy-public/chispavision-mc2:final-512`

Immutable digest:

`sha256:dbfcaf89fc2d47823406c1ceeefef464a98a7e4328226511ab1625c3d721868f`

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
- Streamlit
- HyperLoom research lane
- AMD Radeon AI PRO R9700

## One-line pitch

**From difficult pixels to exact OCR, then from OCR to machine-readable physical assets on AMD.**

## Demo sequence

1. Open `https://infralens.creatorcore.ai/`.
2. Read a difficult challenge plate/sign in **Challenge OCR**.
3. Show exact OCR + confidence + AMD runtime evidence.
4. Scan a real infrastructure label in **Asset Passport**.
5. Show extracted device metadata and download the structured passport.
6. Upload several field images in **Batch Intake** and show the inventory preview.
7. Show the verified public container reference and immutable digest.
8. Mention the HyperLoom optimization lane only within its preserved evidence boundaries.

## Claim boundary

The final public image and anonymous-pull validation may be cited. Do not claim grader-private accuracy or a HyperLoom speedup unless those specific measurements exist.

The public judge UI is not the grader contract. Visual/UI changes must never require rebuilding the frozen `final-512` artifact.

## Do not submit

Do not use the older 256-token digest `sha256:971f1fd2873f157d1027327b15251d147b0896b5cce2c9bd94820d0ef9337e3e`.
