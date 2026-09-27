# AMD Program Continuity — 2026-09-27

## Purpose

Cross-chat source of truth for the current AMD work. Read this before creating a new AMD repo, changing project identity, or starting a duplicate build.

## Canonical project map

### AMD AI Academy

Program window: 2026-09-01 through 2026-12-01.

Primary R&D repository:
- `Rafa-Innerchispa/hyperloom-r9700-experimental`

Role:
- continuous Radeon AI PRO R9700 / ROCm / HyperLoom research;
- correctness and performance evidence;
- vLLM adaptation work;
- experimental optimization knowledge.

Mini Challenge 2 deliverable:
- `Rafa-Innerchispa/infralens-ocr-amd`

Role:
- strict OCR grader implementation for Mini Challenge 2;
- product extension: physical-infrastructure Asset Passports;
- Field Scanner visual demo;
- optional HyperLoom optimization lane using the OCR workload as a real multimodal optimization target.

Do not use `amd-ralfiia-hybrid-ops-copilot` as the current Academy engineering source of truth. It belongs to earlier AMD history.

### AMD Developer Hackathon ACT III

Separate repository:
- `Rafa-Innerchispa/inneros-amd-act-iii`

Keep ACT III architecture, product narrative and submission artifacts separate from Academy/MC2. HyperLoom/R9700 may be a proving case, not the whole ACT III product.

## Mini Challenge 2 current state

Implemented:
- grader CLI and exact `text/confidence` JSON;
- US and mainland-Chinese plate rules;
- multi-line traffic sign handling;
- deterministic decoding;
- image preprocessing and bounded TTA;
- resident OCR service;
- Asset Passport extension;
- Field Scanner demo;
- HyperLoom/vLLM benchmark lane.

2026-09-27 hardening branch:
- `chatgpt/mc2-finalize-20260927`

Changes:
- raise bounded OCR generation budget from 40 to 256 tokens;
- explicitly detect generation that exhausts the token budget;
- reject truncated candidates rather than returning them as grader answers;
- preserve deterministic decoding;
- record completion evidence in runtime output.

## Required final acceptance

MC2 is not READY_TO_SUBMIT until all are true:

1. mandatory ROCm base builds successfully;
2. exact final container runs on physical Radeon AI PRO R9700;
3. real OCR inference passes challenge-like fixtures;
4. per-image latency is under challenge limit;
5. startup and VRAM are within challenge limits;
6. final image size is within challenge limit;
7. public image can be pulled anonymously;
8. grader CLI/output passes again from the anonymously pulled image;
9. final image digest and evidence are recorded here.

## Parallel HyperLoom rule

HyperLoom R9700 work continues in parallel and is not considered finished. vLLM 0.30 source/static work does not count as physical R9700 proof. MC2 must not wait for full HyperLoom completion.

## Handoff rule

At the end of every substantial AMD session, record:
- repo / branch / SHA;
- what is physically verified vs static-only;
- active image/container/build;
- blocker;
- next acceptance gate;
- submission state;
- evidence paths.

A new chat should read this file first.
