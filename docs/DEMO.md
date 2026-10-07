# InfraLens Field Scanner Demo

The AMD grader uses the strict CLI/container contract. The visual demo is intentionally separate so presentation code cannot alter the graded output.

## What the demo shows

1. **Challenge OCR** — upload a license plate or road sign and show recognized text + confidence.
2. **Asset Passport** — reuse the same OCR result to identify physical-infrastructure metadata such as brand, model, serial, MAC/IP and electrical ratings.
3. **Batch Intake** — upload several equipment photos and preview a structured inventory table.

## Deployed demo endpoint

Current AMD 1.5 deployment:

- Tailscale / remote: `http://100.72.153.124:18501`
- Home LAN: `http://192.168.1.5:18501`
- Frontend: Streamlit `demo/app.py`
- Frontend port: `18501`
- Backend is local-only behind the frontend deployment and should not be exposed publicly.

Use the Tailscale URL when reviewing the demo from outside the home LAN.

Last cross-host network validation recorded on 2026-10-06 confirmed the LAN and Tailscale frontend paths returned HTTP 200 after the AMD 1.5 route-overlap fix. Re-check live reachability before final submission if the host or Tailscale routing changes.

## Run

Start the canonical ROCm OCR container/service first, then:

```bash
python -m pip install -r demo/requirements.txt
streamlit run demo/app.py
```

By default the UI calls:

```text
http://127.0.0.1:8765/ocr
```

Override with `INFRALENS_OCR_URL` if the resident service is exposed elsewhere.

## Judge story

The demo should show one challenge image and one real infrastructure label. The key transition is:

```text
difficult pixels -> exact OCR -> structured physical asset
```

The first half satisfies Mini Challenge 2. The second half demonstrates why InfraLens is useful beyond the challenge.

## Next session checkpoint

Do not reopen the frozen `final-512` challenge artifact.

Next session starts here:

1. Open `http://100.72.153.124:18501` over Tailscale.
2. Review the final visual polish only.
3. Test one challenge OCR image.
4. Test one real infrastructure/equipment label in Asset Passport mode.
5. Test Batch Intake with multiple images.
6. Capture final demo screenshots/video if the UI is approved.
7. Confirm the Lablab MC2 submission state and submit/update only the presentation metadata if needed.
8. Then move to Mini Challenge 3 RAG.

The grader artifact and its immutable digest remain frozen and must not be rebuilt as part of UI review.
