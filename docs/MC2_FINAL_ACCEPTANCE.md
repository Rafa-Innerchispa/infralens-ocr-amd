# Mini Challenge 2 Final Acceptance Checklist

A submission is READY only when every required gate below has evidence.

- [ ] clean repository state based on current remote main
- [ ] static tests / compile pass
- [ ] deterministic stub contract pass
- [ ] challenge normalization tests pass
- [ ] final Docker build succeeds from mandated ROCm base
- [ ] container starts on Radeon AI PRO R9700
- [ ] runtime reports ROCm/HIP GPU path
- [ ] warmup succeeds
- [ ] real plate OCR succeeds
- [ ] real multi-line sign OCR succeeds
- [ ] long-output/truncation fixture completes without selected truncation
- [ ] every grader JSON contains exactly required text/confidence schema
- [ ] each image <30 seconds
- [ ] startup <10 minutes
- [ ] peak VRAM within challenge limit
- [ ] image uncompressed size within challenge limit
- [ ] no API keys/tokens/.env embedded
- [ ] public registry push succeeds
- [ ] anonymous pull succeeds
- [ ] acceptance suite passes on anonymously pulled image
- [ ] README and submission copy match measured evidence
- [ ] no performance/accuracy claim without evidence artifact
