# HyperLoom Optimization Lane

InfraLens is not coupled to HyperLoom in the AMD Mini Challenge 2 grader image.

Instead, the repository defines an **optional optimization lane** where the same OCR workload is served through vLLM on the Radeon AI PRO R9700 and evaluated with the same evidence discipline used by the HyperLoom R9700 research line.

This preserves the strict challenge container while giving the project a second, research-grade story:

> **Can HyperLoom make a real multimodal OCR workload faster on AMD hardware without changing a single expected OCR answer?**

## Why this fits

HyperLoom is designed around:

- workload profiling,
- bottleneck discovery,
- iterative optimization,
- benchmark validation,
- correctness-preserving promotion.

InfraLens gives HyperLoom a practical multimodal workload rather than a synthetic text benchmark.

Current vLLM supports Qwen2.5-VL multimodal inference, including image inputs, and exposes ROCm attention backends. That makes an isolated vLLM lane technically appropriate for experimentation without changing the grader-facing implementation.

## What we reuse from the R9700 work

We intentionally reuse the **method**, not model-specific patches.

Reusable:

- exact baseline vs candidate comparison,
- fresh-process vs hot-runtime measurements,
- deterministic output comparison,
- p50/p95 latency,
- throughput under concurrency,
- VRAM observation,
- explicit backend/runtime fingerprint,
- bounded candidate lane,
- restore-to-known-good rule,
- evidence before promotion.

Not reusable by assumption:

- the Qwen3-Coder WNA16 MoE patch,
- Qwen3-Coder-specific tuned configs,
- any previously measured speedup percentage.

InfraLens uses a different multimodal model and must earn its own result.

## Research question

**Baseline:** Qwen2.5-VL-3B challenge OCR workload.

**Candidate:** same model + same prompts + same images, served through a HyperLoom-observed vLLM/ROCm lane on R9700.

A candidate is interesting only if:

1. every expected OCR answer remains identical or improves,
2. the same challenge normalization rules are applied,
3. latency/throughput improves measurably,
4. the optimized AMD execution path is evidenced,
5. the result is reproducible across repeated runs.

## Optimization dimensions

HyperLoom may explore bounded settings such as:

- ROCm attention backend,
- image pixel budget,
- multimodal processor/cache behavior,
- batch/concurrency shape,
- warmup strategy,
- scheduler configuration,
- dtype,
- GPU queue behavior,
- request grouping,
- resident-server lifecycle.

No configuration is promoted because it merely "looks faster."

## Benchmark matrix

At minimum collect:

| Metric | Baseline | Candidate |
| --- | ---: | ---: |
| Exact OCR matches | | |
| p50 latency | | |
| p95 latency | | |
| cold first request | | |
| warm request median | | |
| requests/min | | |
| peak VRAM | | |
| runtime/backend fingerprint | | |

## Promotion gate

A candidate is **PASS** only when:

- OCR exact-match score is not lower than baseline,
- no required challenge output is missing,
- latency/throughput claim is supported by repeated measurements,
- backend/runtime evidence is recorded,
- the baseline can be restored.

## Judge-facing story

The Mini Challenge submission remains simple:

> InfraLens performs OCR on AMD ROCm and turns the result into an Asset Passport.

The optional research extension is:

> We then used the same real OCR workload as a HyperLoom optimization target on a physical Radeon AI PRO R9700, asking the optimizer to improve performance without sacrificing exact OCR correctness.

That connects the Academy projects naturally: one project creates a useful AMD workload; the other teaches an agentic optimization system how to make that workload run better.
