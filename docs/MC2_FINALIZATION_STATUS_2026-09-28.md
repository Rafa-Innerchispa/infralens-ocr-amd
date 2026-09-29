# MC2 Finalization Status — 2026-09-28

## Verdict

**NOT YET READY TO SUBMIT.**

The implementation works physically on the Radeon AI PRO R9700, but the exact hardened reproducible artifact is still completing its final build/export and has not yet passed public-registry anonymous-pull validation.

## Canonical source

Repository: `Rafa-Innerchispa/infralens-ocr-amd`

Branch: `chatgpt/mc2-final-512-20260928`

Candidate SHA: `ee10e7f093bc1bc62e964ec8c177e47fd7b1a107`

## Mandated runtime base

`rocm/pytorch:rocm10.0_ubuntu26.04_py3.14_pytorch_release_2.13.0`

Observed local base digest:

`sha256:3174cb7061d94c427da96c0edef4adea28046fa3f3b2ff3948dc4e995665ff8c`

## Model

`Qwen/Qwen2.5-VL-3B-Instruct`

Pinned revision:

`66285546d2b821cf421d4f5eb2576359d3770cd3`

Final generation ceiling:

`512` tokens.

## Why 512

Long road signs can require more output budget than short license plates. The final branch combines the 512 ceiling with explicit EOS completion logic: a faster or shorter generation is not accepted merely because it emitted some plausible text.

## Physical proof from previous 512 candidate

- GPU: AMD Radeon AI PRO R9700
- architecture: gfx1201
- container healthy
- GPU recognized by PyTorch/ROCm
- VRAM used with resident OCR model: ~8.9 GB
- US plate: PASS, 1.644 s
- ROAD WORK AHEAD: PASS, 1.774 s
- 35 advisory plaque: PASS, 1.303 s

## Exact reproducible rebuild

Target local image:

`infralens-ocr-amd:mc2-final-ee10e7f`

Build state at document creation:

- Python dependencies installed
- exact pinned model downloaded
- application copied
- filesystem preparation completed
- Docker exporting final layers

The build is intentionally allowed to complete before any new GPU test begins.

## Known registry state

Registry repository:

`us-central1-docker.pkg.dev/innerops-agentic-platform/amd-academy-public`

A previous image exists there, but it is not the final 512/EOS artifact.

An attempted push of the previous local 512 image failed with:

`authentication failed`

This is a delivery/authentication issue, not an OCR runtime failure.

## Final delivery gate

The submission's image field must remain unset until:

- final exact image passes on physical R9700
- exact image is pushed successfully
- an anonymous client with empty Docker config can pull it
- pulled digest is re-run successfully
