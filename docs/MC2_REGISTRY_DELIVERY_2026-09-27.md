# MC2 Public Registry Delivery Notes

Updated: 2026-09-27

## Why registry selection matters

The AMD Mini Challenge 2 image must be publicly pullable by the evaluation infrastructure. The mandated ROCm base must remain intact; flattening or splitting base layers is not an acceptable workaround.

Mandatory base:

`rocm/pytorch:rocm10.0_ubuntu26.04_py3.14_pytorch_release_2.13.0`

Manifest digest:

`sha256:3174cb7061d94c427da96c0edef4adea28046fa3f3b2ff3948dc4e995665ff8c`

The base contains eleven layers. Its largest compressed layer is:

- digest: `sha256:1e78e706bbca418f66beaf7117c07e22a2a1b950d6b23b03ff63ba3b74fa07d3`
- compressed bytes: `19,956,931,520`
- approximately 18.6 GiB

## Consequences

Do not assume every OCI registry accepts this layer.

Known public limits checked on 2026-09-27:

- Amazon ECR Public: 10,000 MiB maximum layer, therefore incompatible.
- Google Artifact Registry: maximum artifact size is documented as 5 TB; large uploads require an authentication method that will not expire mid-upload.
- Azure Container Registry: documents a 195 GiB maximum image-layer size.
- GHCR is not selected for this delivery lane because its documented layer limit is below the mandated layer.

Docker Hub remains a candidate because the mandatory base itself is hosted there, but final compatibility must be proven by an actual push and anonymous pull. Do not declare it supported from assumption.

## Acceptance rule

A registry is accepted only after:

1. exact final image is pushed by immutable digest;
2. a clean Docker client with no registry credentials pulls that digest anonymously;
3. pulled manifest preserves the mandatory base-layer prefix;
4. pulled image re-runs the grader CLI and physical acceptance tests.

No registry reference belongs in the Lablab submission until these checks pass.

## Current strategy

1. Finish and physically validate the local R9700 image first.
2. Attempt the least-complex compatible public registry using existing authorized accounts.
3. If Docker Hub cannot preserve/publish the oversized base layer, use a registry whose documented layer limit accepts it rather than flattening the base.
