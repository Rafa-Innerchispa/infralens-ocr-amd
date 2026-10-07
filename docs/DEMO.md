# InfraLens Field Scanner Demo

The AMD grader uses the strict CLI/container contract. The visual demo is intentionally separate so presentation code cannot alter the graded output.

## What the demo shows

1. **Challenge OCR** — upload a license plate or road sign and show recognized text + confidence.
2. **Asset Passport** — reuse the same OCR result to identify physical-infrastructure metadata such as brand, model, serial, MAC/IP and electrical ratings.
3. **Batch Intake** — upload several equipment photos and preview a structured inventory table.

## Deployed demo endpoint

Current AMD 1.5 deployment:

- **Judge/public URL:** `https://infralens.creatorcore.ai/`
- Tailscale / operator access: `http://100.72.153.124:18501`
- Home LAN: `http://192.168.1.5:18501`
- Frontend: Streamlit `demo/app.py`
- Frontend port: `18501`
- OCR backend remains private behind the frontend and must not be exposed publicly.

Use the public HTTPS URL for Lablab/judge review. Use Tailscale only for operator troubleshooting.

### Live verification

Verified on 2026-10-07 from the AMD/Cloudflare control path:

- Cloudflare zone `creatorcore.ai`: credentials and DNS permissions available.
- `https://infralens.creatorcore.ai/`: HTTP 200.
- Response server: Cloudflare.
- Application response: Streamlit HTML.
- AMD frontend port `18501`: listening.
- `infralens-track2-ui`: running.
- `infralens-track2-ocr`: running and healthy.

The immutable grader artifact remains separate from this presentation endpoint.

## Run

Start the canonical ROCm OCR container/service first, then:

```bash
python -m pip install -r demo/requirements.txt
streamlit run demo/app.py
```

By default the repository demo calls:

```text
http://127.0.0.1:8765/ocr
```

The deployed Track 2 stack overrides the backend target for the resident OCR service. Do not expose the OCR backend publicly.

## Judge story

The demo should show one challenge image and one real infrastructure label. The key transition is:

```text
difficult pixels -> exact OCR -> structured physical asset
```

The first half satisfies Mini Challenge 2. The second half demonstrates why InfraLens is useful beyond the challenge.

## MC2 closeout checkpoint

Do not reopen the frozen `final-512` challenge artifact.

Finish MC2 in this order:

1. Open `https://infralens.creatorcore.ai/` exactly as a judge would.
2. Review the final visual polish only.
3. Test one challenge OCR image.
4. Test one real infrastructure/equipment label in Asset Passport mode.
5. Test Batch Intake with multiple images.
6. Capture final demo screenshots/video if the UI is approved.
7. Confirm the Lablab MC2 submission state and submit/update only presentation metadata if needed.
8. Only after MC2 is closed, move to Mini Challenge 3.

The grader artifact and its immutable digest remain frozen and must not be rebuilt as part of UI review.
