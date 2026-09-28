# AMD Program Continuity — 2026-09-28

This file is the canonical context anchor for the AMD workstreams. Update it when a major decision, submission state, runtime gate, or repository role changes.

## Repository map

- **AMD AI Academy / HyperLoom R9700 R&D:** `Rafa-Innerchispa/hyperloom-r9700-experimental`
- **AMD AI Academy Mini Challenge 2 submission:** `Rafa-Innerchispa/infralens-ocr-amd`
- **AMD Developer Hackathon ACT III:** `Rafa-Innerchispa/inneros-amd-act-iii`
- `Rafa-Innerchispa/infralens-ocr` is a superseded prototype and must not be submitted.
- Older AMD/ACT II material such as `amd-ralfiia-hybrid-ops-copilot` is historical, not the current ACT III canonical repo.

## Mini Challenge 2

Product story: difficult visual text -> exact OCR -> structured physical Asset Passport.

Judge-facing layers:
1. strict AMD grader contract for plates and road signs,
2. Field Scanner visual demo,
3. optional Asset Passport for real infrastructure,
4. optional HyperLoom optimization lane that must preserve OCR correctness.

Current model baseline: `Qwen/Qwen2.5-VL-3B-Instruct`.

Mandatory container base:
`rocm/pytorch:rocm10.0_ubuntu26.04_py3.14_pytorch_release_2.13.0`

Hard gates before submission:
- final image builds from current main,
- real inference on physical Radeon AI PRO R9700 / ROCm,
- startup < 10 minutes,
- each challenge image < 30 seconds,
- peak VRAM within challenge limits,
- image size within challenge limits,
- exact required JSON output,
- public registry push,
- anonymous pull of the exact submitted image,
- rerun acceptance from pulled image.

## OCR hardening decision

Short generation ceilings can truncate long road-sign transcriptions. The challenge implementation therefore uses a generous generation ceiling and records whether generation hit that ceiling without EOS. Truncated candidates are penalized and never preferred over a complete candidate solely because their token probabilities are high.

## HyperLoom relationship

Do not copy Qwen3-Coder-specific WNA16/MoE patches into InfraLens by assumption. Reuse HyperLoom's methodology:
baseline -> profile -> candidate -> correctness gate -> benchmark -> evidence -> promotion.

InfraLens is a useful multimodal workload for future HyperLoom R9700 optimization experiments. HyperLoom vLLM 0.30 work continues in parallel and must not block MC2 submission.

## ACT III

ACT III is a separate flagship hackathon. Keep `inneros-amd-act-iii` isolated from Academy deliverables. The current concept should leverage the R9700/HyperLoom experience, but final scope must be aligned to official ACT III tracks/judging when published.

## Continuity rule

Do not reconstruct these relationships from chat history. Read this file and the current git history first.
