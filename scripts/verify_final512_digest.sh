#!/usr/bin/env bash
# Verify the local final-512 image digest matches the validated competition artifact.
set -euo pipefail

IMAGE="us-central1-docker.pkg.dev/innerops-agentic-platform/amd-academy-public/chispavision-mc2:final-512"
EXPECTED="sha256:dbfcaf89fc2d47823406c1ceeefef464a98a7e4328226511ab1625c3d721868f"

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  echo "FAIL: image not present locally: $IMAGE" >&2
  exit 1
fi

ACTUAL="$(docker image inspect "$IMAGE" --format '{{index .RepoDigests 0}}' | cut -d@ -f2)"
if [[ -z "$ACTUAL" ]]; then
  ACTUAL="$(docker image inspect "$IMAGE" --format '{{.Id}}')"
fi

if [[ "$ACTUAL" != "$EXPECTED" && "$ACTUAL" != "${EXPECTED#sha256:}" ]]; then
  echo "FAIL: digest mismatch" >&2
  echo "  expected: $EXPECTED" >&2
  echo "  actual:   $ACTUAL" >&2
  exit 1
fi

echo "OK: final-512 digest unchanged ($EXPECTED)"
