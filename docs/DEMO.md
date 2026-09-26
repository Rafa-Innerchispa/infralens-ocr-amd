# InfraLens Field Scanner Demo

The AMD grader uses the strict CLI/container contract. The visual demo is intentionally separate so presentation code cannot alter the graded output.

## What the demo shows

1. **Challenge OCR** — upload a license plate or road sign and show recognized text + confidence.
2. **Asset Passport** — reuse the same OCR result to identify physical-infrastructure metadata such as brand, model, serial, MAC/IP and electrical ratings.
3. **Batch Intake** — upload several equipment photos and preview a structured inventory table.

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
