# Mini Challenge 2 Finalization Checklist

Updated: 2026-09-28

## Current verdict

**LOCAL / PHYSICAL R9700 ACCEPTANCE: PASS**

Exact evidence is recorded in [MC2_PHYSICAL_ACCEPTANCE_2026-09-28.md](MC2_PHYSICAL_ACCEPTANCE_2026-09-28.md).

Validated image:
- tag: `infralens-ocr-amd:mc2-final-7ec068b700a7`
- local digest: `sha256:971f1fd2873f157d1027327b15251d147b0896b5cce2c9bd94820d0ef9337e3e`
- GPU: AMD Radeon AI PRO R9700 (`gfx1201`)

## P0 — correctness and packaging

- [x] Canonical repository identified: `Rafa-Innerchispa/infralens-ocr-amd`.
- [x] Duplicate prototype marked non-canonical.
- [x] Grader CLI implemented.
- [x] Exact grader JSON isolated from Asset Passport.
- [x] Deterministic decoding.
- [x] Output budget raised above the original 40-token cap.
- [x] Incomplete-generation detection added.
- [x] Explicit EOS required.
- [x] Fail closed when OCR generation is incomplete/truncated.
- [x] Runtime dependencies pinned.
- [x] Qwen2.5-VL-3B model revision pinned.
- [x] CI passes on finalization branch head.
- [x] Mandatory ROCm container built from final code.
- [x] Mandatory base preserved.
- [x] Image size under challenge limit: 24.673 GiB.

## P0 — physical R9700 acceptance

- [x] Final container started on Radeon AI PRO R9700.
- [x] ROCm/PyTorch physical GPU path verified.
- [x] Runtime/GFX fingerprint recorded: R9700 / `gfx1201`.
- [x] Warmup/startup completed.
- [x] US plate fixtures passed.
- [x] Multi-line road/work-zone sign fixtures passed.
- [x] Advisory numeric plaque fixtures passed.
- [x] Blur/degraded plate fixture passed.
- [x] Large sign fixture passed.
- [x] Required grader JSON remained exact.
- [x] Exact-match acceptance corpus: 6/6 PASS.
- [x] No incomplete/truncated generation accepted.

## P0 — measured limits

- [x] Container startup measured: 50.340 s (< 600 s).
- [x] Every measured image under 30 s.
- [x] Observed per-image range: 1.687–4.072 s.
- [x] Peak VRAM measured: 17,829 MiB (< 48 GiB).
- [x] Image size measured: 24.673 GiB (< 60 GiB).
- [ ] Record formal warm p50 latency.
- [ ] Record formal warm p95 latency.

## P0 — delivery

- [ ] Push immutable final image to a compatible public registry.
- [ ] Record public immutable digest.
- [ ] Anonymous pull exact digest in a clean environment.
- [ ] Verify mandatory base-layer lineage after pull.
- [ ] Re-run grader CLI against anonymously pulled image.
- [ ] Record registry-delivery PASS evidence.
- [ ] Only then place the public image reference in the Lablab submission.

## P1 — presentation

- [x] Field Scanner visual demo exists.
- [x] Asset Passport extension exists.
- [x] HyperLoom optimization lane documented.
- [x] Actual AMD runtime evidence exists.
- [ ] Capture one polished challenge OCR demo.
- [ ] Capture one real PC Doctor/VigilOS equipment-label demo.
- [ ] Add baseline-vs-optimized HyperLoom panel only after real comparative measurements exist.

## Parallel work

HyperLoom R9700 continues separately in `Rafa-Innerchispa/hyperloom-r9700-experimental`.

AMD Developer Hackathon ACT III remains separate in `Rafa-Innerchispa/inneros-amd-act-iii`.
