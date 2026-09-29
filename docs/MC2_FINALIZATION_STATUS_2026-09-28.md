# MC2 Finalization Status — 2026-09-28

## Verdict

**READY TO SUBMIT.**

The hardened 512-token MC2 source has been merged into canonical `main` and the exact artifact has passed the full delivery chain:

1. exact reproducible build from source candidate `ee10e7f093bc1bc62e964ec8c177e47fd7b1a107`;
2. physical validation on AMD Radeon AI PRO R9700 (`gfx1201`);
3. authenticated publication to Google Artifact Registry;
4. anonymous pull using an empty Docker configuration;
5. second physical execution on the R9700 using the public registry artifact;
6. canonical source integration through PR #3, merge commit `8343fce02856491e42a1b10dc266d77cdbc102b3`.

## Canonical source

- Repository: `Rafa-Innerchispa/infralens-ocr-amd`
- Canonical branch: `main`
- Hardened source candidate: `ee10e7f093bc1bc62e964ec8c177e47fd7b1a107`
- MC2 merge commit: `8343fce02856491e42a1b10dc266d77cdbc102b3`
- Model: `Qwen/Qwen2.5-VL-3B-Instruct`
- Model revision: `66285546d2b821cf421d4f5eb2576359d3770cd3`
- Generation ceiling: `512`
- Runtime base: `rocm/pytorch:rocm10.0_ubuntu26.04_py3.14_pytorch_release_2.13.0`

## Verified public artifact

`us-central1-docker.pkg.dev/innerops-agentic-platform/amd-academy-public/chispavision-mc2:final-512`

Immutable digest:

`sha256:dbfcaf89fc2d47823406c1ceeefef464a98a7e4328226511ab1625c3d721868f`

The pulled image config independently confirms `OCR_MAX_NEW_TOKENS=512` and the pinned model revision.

The older digest `sha256:971f1fd2873f157d1027327b15251d147b0896b5cce2c9bd94820d0ef9337e3e` is a superseded 256-token artifact and must not be submitted.

## Exact local-artifact validation on R9700

| Fixture | Expected | Result | Warm latency |
| --- | --- | --- | ---: |
| US plate | `8ABC123` | `8ABC123` | 1.705 s |
| Work sign | `ROAD WORK AHEAD` | `ROAD WORK AHEAD` | 1.868 s |
| Advisory plaque | `35` | `35` | 1.354 s |

## Public-artifact revalidation on R9700

| Fixture | Expected | Result | Warm latency |
| --- | --- | --- | ---: |
| US plate | `8ABC123` | `8ABC123` | 1.666 s |
| Work sign | `ROAD WORK AHEAD` | `ROAD WORK AHEAD` | 1.721 s |
| Advisory plaque | `35` | `35` | 1.307 s |

All six final acceptance invocations returned rc=0 and exact text.

## Runtime notes

- GPU: AMD Radeon AI PRO R9700
- GFX: `gfx1201`
- Resident model VRAM observed: approximately 8.9 GB per container
- Deterministic generation
- Explicit EOS completion required
- Incomplete or truncated generations fail closed
- Model embedded for offline runtime

## Submission rule

Use only the verified `:final-512` public reference above, preferably together with the immutable digest in evidence. Do not use the stale 256-token digest or the superseded prototype repository.
