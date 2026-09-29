# Track 2 Product Continuation — 2026-09-28

## Identity

Track 2 in the current AMD Academy context is Mini Challenge 2 / InfraLens OCR.

Canonical repository:
- Rafa-Innerchispa/infralens-ocr-amd

Submission artifact is frozen and must not be modified:
- public tag: us-central1-docker.pkg.dev/innerops-agentic-platform/amd-academy-public/chispavision-mc2:final-512
- digest: sha256:dbfcaf89fc2d47823406c1ceeefef464a98a7e4328226511ab1625c3d721868f

## Current implemented product layer

The repository already includes, beyond the grader OCR core:

1. Asset Passport extraction
   - infrastructure asset type detection
   - brand detection
   - serial/model extraction
   - MAC/IP extraction
   - voltage/current/power extraction
   - runtime evidence embedded in the passport

2. Field Scanner demo
   - local-only OCR service consumption
   - image preview
   - OCR confidence
   - recognized text
   - runtime evidence
   - downloadable Asset Passport JSON

3. Batch Intake
   - multiple image upload
   - inventory preview
   - file/text/confidence/asset type/brand aggregation

## Product continuation lane

Development branch:
- chatgpt/mc2-track2-product-20260928

This lane must not alter the verified challenge artifact unless a separate acceptance cycle is explicitly run.

## Next implementation gates

P0:
- persist Batch Intake as a reproducible inventory bundle
- add CSV + JSON batch export
- add SHA-256 evidence per source image/result
- preserve local-only execution
- add deterministic tests for Asset Passport entities and batch inventory serialization

P1:
- add source-image metadata and capture timestamp
- add asset deduplication hints using serial/MAC/model identifiers
- add evidence bundle suitable for FieldOps/VigiLOS ingestion
- add explicit schema versioning and import/export examples

P2:
- connect the product layer to HyperLoom benchmark methodology without changing grader output
- compare baseline vs candidate only when correctness is preserved
- capture p50/p95, throughput, VRAM, runtime/backend fingerprint

## Truth boundary

The competition OCR artifact is already physically validated on the Radeon AI PRO R9700 and anonymously pullable from the public registry.

Product/demo improvements after this point are a separate continuation lane and must not be presented as part of the already-verified container unless they are rebuilt and revalidated independently.
