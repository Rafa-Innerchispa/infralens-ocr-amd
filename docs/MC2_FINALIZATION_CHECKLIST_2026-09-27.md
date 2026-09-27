# Mini Challenge 2 Finalization Checklist

## P0 — correctness and packaging

- [x] Canonical repository identified: `Rafa-Innerchispa/infralens-ocr-amd`.
- [x] Duplicate prototype marked non-canonical.
- [x] Grader CLI implemented.
- [x] Exact grader JSON isolated from Asset Passport.
- [x] Deterministic decoding.
- [x] Raise output budget above original 40-token cap.
- [x] Add incomplete-generation detection.
- [x] Fail closed when every OCR pass is truncated.
- [ ] Run CI for finalization branch.
- [ ] Sync finalization branch into isolated AMD build lane.
- [ ] Build mandatory ROCm container from final branch.
- [ ] Verify exact mandatory base lineage.

## P0 — physical R9700 acceptance

- [ ] Start final container on Radeon AI PRO R9700.
- [ ] Verify ROCm/PyTorch sees the physical R9700.
- [ ] Record runtime fingerprint.
- [ ] Run warmup.
- [ ] Run plate fixtures.
- [ ] Run mainland-Chinese plate fixtures.
- [ ] Run multi-line road/work-zone sign fixtures.
- [ ] Run advisory numeric plaques.
- [ ] Run blur/glare/perspective/JPEG degradation fixtures.
- [ ] Run at least one large-resolution image.
- [ ] Confirm no stale output between repeated docker exec calls.
- [ ] Confirm no incomplete generation is accepted.

## P0 — limits

- [ ] Measure container startup time.
- [ ] Measure warm p50 latency.
- [ ] Measure warm p95 latency.
- [ ] Confirm each image under challenge latency limit.
- [ ] Record peak VRAM.
- [ ] Record compressed and uncompressed image size.
- [ ] Confirm final image under challenge size limit.

## P0 — delivery

- [ ] Push immutable final tag to public registry.
- [ ] Record digest.
- [ ] Anonymous pull exact digest in a clean environment.
- [ ] Re-run grader CLI against anonymously pulled image.
- [ ] Record final PASS evidence.
- [ ] Only then submit Lablab MC2.

## P1 — presentation

- [x] Field Scanner visual demo exists.
- [x] Asset Passport extension exists.
- [x] HyperLoom optimization lane documented.
- [ ] Capture one challenge OCR demo.
- [ ] Capture one real PC Doctor/VigilOS equipment-label demo.
- [ ] Show actual AMD runtime evidence.
- [ ] Add measured baseline/optimized panel only if real data exists.

## Parallel work

HyperLoom R9700 continues separately in `hyperloom-r9700-experimental`. ACT III remains separate in `inneros-amd-act-iii`.
