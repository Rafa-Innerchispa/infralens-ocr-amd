# AMD Program Continuity — 2026-09-28

This file is the canonical cross-chat handoff for the current AMD work. Do not reconstruct this context from chat history.

## Program map

### AMD AI Academy — three-month program

Primary R&D repository:

- `Rafa-Innerchispa/hyperloom-r9700-experimental`

The Academy is the umbrella program. HyperLoom R9700 remains the long-running AMD/RDNA4 research line.

### Academy Mini Challenge 2 — current deliverable

Canonical repository:

- `Rafa-Innerchispa/infralens-ocr-amd`

This repository is the only submission source for Mini Challenge 2.

The old `Rafa-Innerchispa/infralens-ocr` repository is a superseded prototype and must not be submitted.

### AMD Developer Hackathon ACT III

Separate project/repository:

- `Rafa-Innerchispa/inneros-amd-act-iii`

ACT III is not Mini Challenge 2 and must remain architecturally separate until the official tracks are final.

## MC2 product story

InfraLens / ChispaVision turns visual text into physical-infrastructure data:

```text
image
  -> AMD ROCm vision OCR
  -> exact challenge text
  -> optional Asset Passport
  -> FieldOps / Vigilos / InnerOS
```

Judge-facing demo layers:

1. Challenge OCR
2. Asset Passport
3. Batch Intake / Field Scanner
4. optional HyperLoom optimization evidence

The grader-facing JSON remains minimal and isolated from product/demo features.

## HyperLoom relationship

Do not copy Qwen3-Coder-specific WNA16 patches into the OCR model.

Reuse the HyperLoom methodology:

- baseline vs candidate
- cold vs warm measurement
- exact-output correctness gate
- p50/p95 latency
- throughput
- VRAM
- runtime/backend fingerprint
- reject performance candidates that regress correctness

InfraLens is intended to become a real multimodal workload for the R9700 HyperLoom research line.

## Current MC2 finalization branch

Branch:

`chatgpt/mc2-final-512-20260928`

Source lineage:

- `7ec068b700a7d043fa1eb02e1f3800c955eea1f4` — hardened MC2 history
- `28af8ae52a2734db9be2fb49dcd81d6cb4b89e16` — 512 Docker ceiling
- `1ca35e7b962502b7ceb901f48988da75aeb05d91` — 512 engine default
- `ee10e7f093bc1bc62e964ec8c177e47fd7b1a107` — cache-friendly reproducible final Dockerfile

Current candidate source SHA:

`ee10e7f093bc1bc62e964ec8c177e47fd7b1a107`

## Physical evidence already obtained

A previous 512-token candidate image was run on the physical:

- AMD Radeon AI PRO R9700
- gfx1201
- PyTorch 2.13.0 + ROCm 10
- HIP runtime reported by PyTorch: 7.15.26333

Resident model VRAM observed: approximately 8.9 GB.

Controlled fixtures:

| Fixture | Expected | Result | Warm latency |
| --- | --- | --- | ---: |
| US plate | `8ABC123` | `8ABC123` | 1.644 s |
| Work sign | `ROAD WORK AHEAD` | `ROAD WORK AHEAD` | 1.774 s |
| Advisory plaque | `35` | `35` | 1.303 s |

All three were PASS on the physical R9700.

That older image is evidence only. Final submission must use the reproducible hardened `ee10e7f` source or a later verified descendant.

## Reproducibility hardening

The hardened source pins:

- model: `Qwen/Qwen2.5-VL-3B-Instruct`
- model revision: `66285546d2b821cf421d4f5eb2576359d3770cd3`
- Python dependencies
- mandated ROCm base
- explicit EOS completion gate
- bounded generation time
- 512-token final runtime ceiling

## Final acceptance order

Do not call MC2 READY until all gates pass:

1. build exact `ee10e7f` image
2. launch it on physical R9700
3. confirm runtime/backend identity
4. confirm startup < challenge limit
5. run plate/sign/advisory fixtures
6. require exact OCR + explicit completed generation
7. measure warm latency
8. measure VRAM
9. inspect image/manifest size
10. push exact digest to a public registry
11. anonymous pull with empty Docker credentials
12. run pulled digest again on R9700
13. write final evidence bundle
14. merge final branch to main
15. use only the verified public image reference in Lablab

## Registry

Existing Google Artifact Registry:

`us-central1-docker.pkg.dev/innerops-agentic-platform/amd-academy-public`

An older MC2 image has been uploaded there before.

The new 512-token push initially failed because Docker registry authentication was not configured on the AMD node. Do not claim a public final image until authenticated push and anonymous pull both pass.

## Disk safety

The AMD node reached 97% root-disk usage during final image export.

Rules:

- no broad `docker system prune`
- no removal of the mandated ROCm base
- no removal of production service images
- remove only explicitly identified obsolete MC2 artifacts
- preserve at least one physically validated fallback until the reproducible final image passes

## Parallel HyperLoom work

HyperLoom R9700 is not finished. Continue its vLLM 0.30 / RDNA4 physical-validation lane separately after MC2 final submission.

MC2 completion takes priority right now.
