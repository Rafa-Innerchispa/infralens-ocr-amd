# MC2 Finalization Status — 2026-09-28

## Verdict

**TECHNICAL ACCEPTANCE PASSED — READY FOR CANONICAL INTEGRATION.**

The exact hardened 512-token artifact built from source candidate `ee10e7f093bc1bc62e964ec8c177e47fd7b1a107` has now passed physical AMD R9700 validation, authenticated publication, anonymous pull, and a second physical run from the public registry reference.

The only remaining lifecycle gate at this document revision is integrating the final branch into `main` without discarding the independent documentation commits that landed on `main` meanwhile.

## Canonical source

- Repository: `Rafa-Innerchispa/infralens-ocr-amd`
- Finalization branch: `chatgpt/mc2-final-512-20260928`
- Candidate source SHA: `ee10e7f093bc1bc62e964ec8c177e47fd7b1a107`
- Model: `Qwen/Qwen2.5-VL-3B-Instruct`
- Model revision: `66285546d2b821cf421d4f5eb2576359d3770cd3`
- Generation ceiling: `512`
- Runtime base: `rocm/pytorch:rocm10.0_ubuntu26.04_py3.14_pytorch_release_2.13.0`

## Exact local artifact

- Local tag: `infralens-ocr-amd:mc2-final-ee10e7f`
- Local image/index digest: `sha256:dbfcaf89fc2d47823406c1ceeefef464a98a7e4328226511ab1625c3d721868f`
- Created: `2026-09-29T00:39:30.840903631Z`
- Config confirms `OCR_MAX_NEW_TOKENS=512`
- AMD GPU: Radeon AI PRO R9700, gfx1201
- Resident model VRAM observed: approximately 8.9 GB per container

## Physical validation of exact local artifact

| Fixture | Expected | Result | Warm latency |
| --- | --- | --- | ---: |
| US plate | `8ABC123` | `8ABC123` | 1.705 s |
| Work sign | `ROAD WORK AHEAD` | `ROAD WORK AHEAD` | 1.868 s |
| Advisory plaque | `35` | `35` | 1.354 s |

All three returned rc=0.

## Public registry acceptance

Public tag:

`us-central1-docker.pkg.dev/innerops-agentic-platform/amd-academy-public/chispavision-mc2:final-512`

Anonymous Docker pull with an empty Docker config succeeded.

The pulled public tag resolved to the exact final digest:

`sha256:dbfcaf89fc2d47823406c1ceeefef464a98a7e4328226511ab1625c3d721868f`

The pulled image config independently confirmed:

- `OCR_MAX_NEW_TOKENS=512`
- model revision `66285546d2b821cf421d4f5eb2576359d3770cd3`
- final build creation timestamp `2026-09-29T00:39:30.840903631Z`

An older anonymous-pull helper was found to be hardcoded to the previous 256-token digest `sha256:971f1fd2873f157d1027327b15251d147b0896b5cce2c9bd94820d0ef9337e3e`. That stale helper was diagnosed and excluded from final acceptance. The verified `:final-512` tag is the canonical submission artifact.

## Physical validation from the public registry artifact

The public `:final-512` image was launched directly on the Radeon AI PRO R9700 and reached healthy state.

| Fixture | Expected | Result | Warm latency |
| --- | --- | --- | ---: |
| US plate | `8ABC123` | `8ABC123` | 1.666 s |
| Work sign | `ROAD WORK AHEAD` | `ROAD WORK AHEAD` | 1.721 s |
| Advisory plaque | `35` | `35` | 1.307 s |

All three returned rc=0 and exact text.

## Registry authentication repair

The AMD node already had a valid authenticated gcloud configuration, but Docker was not consuming it. A short-lived access token was obtained through the containerized Google Cloud CLI and passed directly to `docker login --password-stdin`; no token was printed or persisted in project documentation.

## Remaining close gate

1. Reconcile the finalization branch with the five independent commits currently on `main`.
2. Merge without force push and preserve both histories.
3. Re-fetch and verify `origin/main` contains the exact hardened source.
4. Mark this document READY TO SUBMIT on canonical `main`.
5. Use only the verified `:final-512` public reference in the challenge submission.
