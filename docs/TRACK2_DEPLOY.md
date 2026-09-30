# InfraLens Track 2 — Persistent Local Deployment (AMD node 1.5)

Deploys ChispaVision / InfraLens as durable local services on **Rafa-Innerchispa/infralens-ocr-amd** without modifying or rebuilding the validated competition artifact **`final-512`**.

## Branch and node

| Item | Value |
|------|-------|
| Git branch | `mc2-track2-deploy-20260928` |
| Deploy commit | `1d3df0a81cbb85950f37aca5946618ef8b37f91d` |
| Host | `ralfiia-amd` (AMD node 1.5) |
| LAN IP | `192.168.1.5` |
| Tailscale IP | `100.72.153.124` |

Record the branch tip SHA after deploy:

```bash
git rev-parse HEAD
```

## Immutable competition image (unchanged)

| Field | Value |
|-------|-------|
| Image | `us-central1-docker.pkg.dev/innerops-agentic-platform/amd-academy-public/chispavision-mc2:final-512` |
| Digest | `sha256:dbfcaf89fc2d47823406c1ceeefef464a98a7e4328226511ab1625c3d721868f` |

Verify before and after any deploy:

```bash
./scripts/verify_final512_digest.sh
```

This deployment **never** runs `docker build` on `final-512` and **never** retags or mutates that image.

## Services and ports

| Service | Container | Port | Bind | Access |
|---------|-----------|------|------|--------|
| OCR backend (ROCm / R9700) | `infralens-track2-ocr` | `18765` | `127.0.0.1` (host network) | Local only |
| Streamlit Field Scanner | `infralens-track2-ui` | `18501` | `0.0.0.0` (host network) | LAN + Tailscale |

Ports `8765` / `8766` remain reserved for existing host services and are **not** used.

### URLs

| Audience | Streamlit UI | OCR (internal) |
|----------|--------------|----------------|
| Same host | http://127.0.0.1:18501 | http://127.0.0.1:18765/ocr |
| LAN | http://192.168.1.5:18501 | — |
| Tailscale | http://100.72.153.124:18501 | — |

`INFRALENS_OCR_URL` for the UI defaults to `http://127.0.0.1:18765/ocr`.

### Public URL status

- Intended public URL: `https://infralens.creatorcore.ai`
- Cloudflare DNS CNAME was created on 2026-09-29 and points to tunnel `6fb8ceab-a17e-41b3-872d-e26ef2d1383f.cfargotunnel.com`.
- Public health currently returns HTTP `404` because the active cloudflared ingress does not yet contain the hostname mapping to `http://192.168.1.5:18501`.
- OCR port `18765` remains private by design.
- Do not expose `18765` publicly and do not rebuild the validated `final-512` image while fixing ingress.
- InnerOS recovery PR `Rafa-Innerchispa/innerops-agentic-platform#108` was merged as `9e7b86d2596f9012ca905b2e686e0d0ac26a662c` after targeted Recovery CI passed. It fixes the stale coordination-state API and adds a dry-run-by-default Cloudflare tunnel ingress upsert.
- Production still needs to deploy/restart that InnerOS commit before the new MCP mutation is available. The required ingress remains exactly `infralens.creatorcore.ai -> http://192.168.1.5:18501`.
- After deploy: apply the ingress, verify HTTPS 200/no `cf-mitigated: challenge`, re-check Streamlit health, OCR health, and the immutable `final-512` digest.
- One-shot production recovery is now canonical in `Rafa-Innerchispa/innerops-agentic-platform` main commit `5eadd4e87e25566146aea66dfeb2dd4d2dd54eb7`: `scripts/deploy_infralens_publication_recovery.sh`. It performs runtime backup/compile/restart, ingress apply, public HTTPS verification, AMD UI/OCR checks, and immutable image verification.

## Deploy

```bash
git checkout mc2-track2-deploy-20260928
cp .env.track2.example .env.track2   # optional overrides
./scripts/verify_final512_digest.sh
docker compose -f docker-compose.track2.yml --env-file .env.track2 up -d
```

First OCR startup loads Qwen2.5-VL on the R9700 and may take up to ~10 minutes (`HEALTHCHECK` start-period in the validated image).

## Validate

Unit / packaging tests (stub backend, no GPU):

```bash
python -m pip install pillow
OCR_BACKEND=stub python scripts/selfcheck.py
python -m unittest discover -s tests -v
```

Generate fixtures and run live checks once OCR is healthy:

```bash
python3 scripts/generate_fixtures.py
./scripts/smoke_track2.sh
python3 scripts/e2e_track2.py
```

Optional unittest hook:

```bash
INFRALENS_LIVE_SMOKE=1 python -m unittest tests.test_track2_deploy -v
```

E2E covers:

1. **Challenge OCR** — `fixtures/e2e/challenge_plate.png`
2. **Asset Passport** — `fixtures/e2e/asset_nvr_label.png`
3. **Batch Intake** — two-image batch via repeated `/ocr` calls
4. **Streamlit** — `/_stcore/health`

## Rollback

Stop Track 2 without touching other stacks or ROCm images:

```bash
docker compose -f docker-compose.track2.yml down
```

Remove only the locally built UI wrapper (optional):

```bash
docker rmi infralens-track2-ui:local
```

Do **not** run `docker system prune` or delete `final-512` / ROCm base images.

Re-verify digest after rollback:

```bash
./scripts/verify_final512_digest.sh
```

## Operations

| Action | Command |
|--------|---------|
| Status | `docker compose -f docker-compose.track2.yml ps` |
| Logs (OCR) | `docker logs -f infralens-track2-ocr` |
| Logs (UI) | `docker logs -f infralens-track2-ui` |
| Restart | `docker compose -f docker-compose.track2.yml restart` |

Both services use `restart: unless-stopped`.

## Proof checklist

- [x] `./scripts/verify_final512_digest.sh` → digest `sha256:dbfcaf89fc2d47823406c1ceeefef464a98a7e4328226511ab1625c3d721868f`
- [x] `curl -sf http://127.0.0.1:18765/health` → `gpu_name: AMD Radeon AI PRO R9700`
- [x] `./scripts/smoke_track2.sh` → Challenge OCR `ABC1234` @ 99.8% confidence
- [x] `python3 scripts/e2e_track2.py` → Challenge OCR, Asset Passport (nvr/Hikvision), Batch Intake, Streamlit
- [x] UI reachable on LAN/Tailscale at `:18501`
- [x] Existing services on `:8765` / `:8766` (RalphiIA QuoteOps) still running

### Deploy evidence (2026-09-29, AMD node 1.5)

| Check | Result |
|-------|--------|
| Base branch tip (pre-deploy) | `3c78636` |
| OCR container | `infralens-track2-ocr` healthy, host network, port `18765` |
| UI container | `infralens-track2-ui` up, port `18501` |
| final-512 rebuilt? | **No** — `pull_policy: never`, digest unchanged |
| GPU | Radeon AI PRO R9700 via ROCm (`torch 2.13.0+rocm10.0.0`) |
