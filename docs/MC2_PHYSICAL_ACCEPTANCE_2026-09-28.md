# MC2 Physical Acceptance — Radeon AI PRO R9700

Date: 2026-09-28

## Final verdict

**PASS — 512-TOKEN PUBLIC ARTIFACT VERIFIED.**

This document supersedes the earlier 256-token acceptance snapshot while preserving it as historical evidence.

## Canonical final artifact

- Repository: `Rafa-Innerchispa/infralens-ocr-amd`
- Canonical branch: `main`
- Hardened source candidate: `ee10e7f093bc1bc62e964ec8c177e47fd7b1a107`
- Merge commit: `8343fce02856491e42a1b10dc266d77cdbc102b3`
- Public image: `us-central1-docker.pkg.dev/innerops-agentic-platform/amd-academy-public/chispavision-mc2:final-512`
- Final digest: `sha256:dbfcaf89fc2d47823406c1ceeefef464a98a7e4328226511ab1625c3d721868f`
- Mandatory base: `rocm/pytorch:rocm10.0_ubuntu26.04_py3.14_pytorch_release_2.13.0`
- Model revision: `66285546d2b821cf421d4f5eb2576359d3770cd3`
- Output ceiling: 512 tokens
- GPU: AMD Radeon AI PRO R9700
- GFX: `gfx1201`

## Exact hardened-image validation

| Fixture | Expected | Result | Latency |
| --- | --- | --- | ---: |
| `us_plate.png` | `8ABC123` | `8ABC123` | 1.705 s |
| `work_sign.png` | `ROAD WORK AHEAD` | `ROAD WORK AHEAD` | 1.868 s |
| `speed_plaque.png` | `35` | `35` | 1.354 s |

All three returned rc=0.

## Anonymous-pull gate

An empty Docker configuration successfully pulled:

`us-central1-docker.pkg.dev/innerops-agentic-platform/amd-academy-public/chispavision-mc2:final-512`

The pull resolved to:

`sha256:dbfcaf89fc2d47823406c1ceeefef464a98a7e4328226511ab1625c3d721868f`

Inspection confirmed `OCR_MAX_NEW_TOKENS=512`.

## Public-artifact physical re-run

The anonymously accessible public artifact was launched directly on the R9700 and reached healthy state.

| Fixture | Expected | Result | Latency |
| --- | --- | --- | ---: |
| `us_plate.png` | `8ABC123` | `8ABC123` | 1.666 s |
| `work_sign.png` | `ROAD WORK AHEAD` | `ROAD WORK AHEAD` | 1.721 s |
| `speed_plaque.png` | `35` | `35` | 1.307 s |

All three returned rc=0.

## Historical 256-token acceptance snapshot

The earlier artifact `sha256:971f1fd2873f157d1027327b15251d147b0896b5cce2c9bd94820d0ef9337e3e` passed a broader six-fixture local corpus and provided useful development evidence, including startup and image-size measurements. It is now superseded for submission because its config used `OCR_MAX_NEW_TOKENS=256`.

Do not use that digest in the final challenge submission.

## Acceptance conclusion

The final 512-token artifact has passed source hardening, local physical execution, registry publication, anonymous pull, and public-artifact physical re-execution on the AMD Radeon AI PRO R9700.
