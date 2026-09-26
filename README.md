# InfraLens OCR

AMD-powered visual asset intelligence for physical infrastructure, packaged for
AMD AI Academy Mini Challenge 2.

InfraLens has two layers:

1. Challenge OCR: a Qwen2.5-VL-3B resident model optimized for the public
   Mini Challenge 2 rules: license plates, road signs, multi-line reading order,
   Chinese plates, numeric advisory plaques and degraded imagery.
2. Asset Passport: an optional deterministic extension that turns recognized
   equipment text into candidate brand/model/serial/MAC/IP/electrical fields
   for field-service inventory.

## Exact grader contract

The Docker image keeps the mandatory base unchanged:

~~~dockerfile
FROM rocm/pytorch:rocm10.0_ubuntu26.04_py3.14_pytorch_release_2.13.0
~~~

The grader-facing command remains:

~~~bash
python3 /app/app.py --input-image /app/input/example.png
~~~

Default output:

~~~text
/app/output/example_output.json
~~~

The graded file contains exactly:

~~~json
{"text":"...","confidence":0.93}
~~~

InfraLens may additionally write an Asset Passport and preview. Those artifacts
are separate and never change the required grader JSON.

## Why a resident VLM

The challenge has hard startup and per-image limits. The container entrypoint
loads Qwen2.5-VL-3B once, warms it, and serves OCR requests locally. Each grader
execution is a thin client, so the model is not reloaded for every image.

A bounded three-variant pass handles common adverse conditions:
original image, contrast-normalized image, and a sharpened/denoised variant.
The time budget prevents extra passes from violating the per-image gate.

## Challenge behavior

Public rules encoded in the prompt and deterministic cleanup include:

- US-style plates: registration only, excluding surrounding state/slogan/URL text.
- Mainland Chinese plates: preserve province character and letter; normalize I/O
  in the serial portion to 1/0.
- Road signs: visible words/numbers in top-to-bottom reading order.
- Numeric advisory plaques: number only when no unit is printed.
- No labels, explanations or markdown in the final OCR text.

For other technical labels, the prompt falls back to literal transcription so
the same engine can power the Asset Passport use case.

## Product extension: Asset Passport

A field technician can photograph a camera, NVR, switch, router, access
controller, inverter or equipment plate. InfraLens preserves the OCR text and
extracts conservative candidate identifiers such as:

- brand
- model number
- serial number
- MAC address
- IPv4 address
- voltage/current/power ratings

The intended future flow is human-confirmed ingestion into InnerOS / FieldOps.

## Build

~~~bash
docker build -t infralens-ocr-amd:mc2 .
~~~

## Run on AMD ROCm

~~~bash
docker run -d --rm \
  --name infralens-ocr \
  --device=/dev/kfd \
  --device=/dev/dri \
  --group-add video \
  --ipc=host \
  -v "$PWD/input:/app/input:ro" \
  -v "$PWD/output:/app/output" \
  infralens-ocr-amd:mc2
~~~

Then:

~~~bash
docker exec infralens-ocr \
  python3 /app/app.py --input-image /app/input/example.png
~~~

## Local contract tests

The stub backend validates packaging without downloading the VLM:

~~~bash
python -m pip install pillow
OCR_BACKEND=stub python scripts/selfcheck.py
python -m unittest discover -s tests -v
~~~


## Field Scanner visual demo

The grader contract remains minimal, but the repository also includes a judge-facing visual product demo:

~~~bash
python -m pip install -r demo/requirements.txt
streamlit run demo/app.py
~~~

The demo has three modes:

- **Challenge OCR** — plate/sign transcription with confidence.
- **Asset Passport** — converts OCR into physical-infrastructure identity such as brand, model, serial, MAC/IP and electrical ratings.
- **Batch Intake** — scans multiple equipment photos into a draft inventory table.

This separation is intentional: presentation features cannot alter or break the strict AMD grader JSON.

## Claim boundaries

This is an experimental AMD AI Academy project. It does not claim official AMD
endorsement. OCR confidence is model evidence, not a guarantee that every
identifier is correct. Asset Passport values should be human-confirmed before
changing operational inventory.
