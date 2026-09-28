# MC2 Physical Acceptance — Radeon AI PRO R9700

Date: 2026-09-28

## Verdict

**PASS**

This evidence corresponds to the exact finalization branch head:

- Branch: `chatgpt/mc2-finalize-20260927`
- Commit: `7ec068b700a7d043fa1eb02e1f3800c955eea1f4`
- Image tag: `infralens-ocr-amd:mc2-final-7ec068b700a7`
- Local image digest: `sha256:971f1fd2873f157d1027327b15251d147b0896b5cce2c9bd94820d0ef9337e3e`
- Mandatory base: `rocm/pytorch:rocm10.0_ubuntu26.04_py3.14_pytorch_release_2.13.0`
- GPU: AMD Radeon AI PRO R9700
- GFX: `gfx1201`

The image was built from the exact branch head after the final truncation/EOS hardening changes.

## Challenge limits

| Gate | Limit | Measured | Result |
|---|---:|---:|---|
| Image size | < 60 GiB | 24.673 GiB | PASS |
| Startup | < 600 s | 50.340 s | PASS |
| Per-image latency | < 30 s | 1.687–4.072 s | PASS |
| Peak VRAM | <= 48 GiB | 17,829 MiB | PASS |
| Grader JSON | exactly text + confidence | exact | PASS |
| Exact fixture match | required for acceptance corpus | 6/6 | PASS |

## Exact-match corpus

| Fixture | Expected | Result | Latency |
|---|---|---|---:|
| `advisory_35.jpg` | `35` | `35` | 2.743 s |
| `plate_blur.jpg` | `5KLM921` | `5KLM921` | 2.598 s |
| `road_closed_large.jpg` | `ROAD CLOSED AHEAD` | same | 4.072 s |
| `road_work_ahead.png` | `ROAD WORK AHEAD` | same | 2.527 s |
| `speed_limit_65.png` | `SPEED LIMIT 65` | same | 2.133 s |
| `us_plate_state.png` | `8ABC123` | same | 1.687 s |

## Runtime notes

- Model: pinned Qwen2.5-VL-3B-Instruct revision `66285546d2b821cf421d4f5eb2576359d3770cd3`
- Deterministic decoding
- Output budget: 256 tokens
- Explicit EOS completion required
- Incomplete/truncated generations fail closed
- Model is embedded for offline runtime
- Resident server loads/warmups once and grader invocations use the strict CLI contract

## Remaining delivery gate

The software and physical R9700 acceptance are complete.

The only remaining P0 delivery gate is public registry publication:

1. push the exact image to a registry that accepts the mandatory ~18.6 GiB compressed ROCm base layer;
2. record immutable public digest;
3. perform an anonymous pull;
4. verify mandatory base-layer lineage;
5. rerun the grader CLI from the anonymously pulled image.

No Lablab image reference should be submitted before that registry gate passes.
