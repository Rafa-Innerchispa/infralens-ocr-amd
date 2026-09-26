# InfraLens OCR

**AMD-powered visual asset intelligence for physical infrastructure.**

InfraLens OCR turns a field photo into two things:

1. the exact Mini Challenge 2 OCR contract required by AMD's grader; and
2. an optional Asset Passport that extracts operational identifiers such as brand, model, serial number, MAC address, IP address, voltage, current and power.

The practical use case is field service: photograph an NVR, camera, access controller, switch, router, inverter, breaker label or equipment plate and convert it into machine-readable inventory for systems such as InnerOS / FieldOps.

## AMD AI Academy Mini Challenge 2

The grading contract is intentionally kept separate from the product extension.

~~~bash
python3 /app/app.py --input-image /app/input/device.jpg
~~~

Required output:

~~~text
/app/output/device_output.json
~~~

with exactly:

~~~json
{"text":"...","confidence":0.92}
~~~

InfraLens additionally writes:

~~~text
/app/output/device_asset_passport.json
/app/output/device_annotated.jpg
~~~

Those extra artifacts are not required by the grader.

## Architecture

~~~text
Field image
   |
   v
lightweight CV line segmentation
   |
   v
TrOCR model loaded once in a local daemon
   |
   +--> graded text + confidence JSON
   |
   +--> deterministic Asset Passport
           brand / model / serial / MAC / IP / electrical values
~~~

The model runs with PyTorch on AMD ROCm. On ROCm, PyTorch exposes AMD GPUs through the familiar torch.cuda API.

## Required AMD base

The Dockerfile intentionally uses the exact Mini Challenge 2 base and must not be flattened or squashed:

~~~dockerfile
FROM rocm/pytorch:rocm10.0_ubuntu26.04_py3.14_pytorch_release_2.13.0
~~~

The OCR model (microsoft/trocr-base-printed) is prefetched during the build so runtime startup is not dependent on Hugging Face network availability.

## Build

~~~bash
docker build -t infralens-ocr-amd:mc2 .
~~~

## Run on an AMD ROCm host

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

Then execute one or more images without reloading the model:

~~~bash
docker exec infralens-ocr python3 /app/app.py --input-image /app/input/device.jpg
~~~

## Local contract test without a model

~~~bash
python -m pip install pillow
OCR_BACKEND=stub python scripts/selfcheck.py
python -m unittest discover -s tests -v
~~~

## Why this is more than a toy OCR demo

Field technicians still type serial numbers, MAC addresses and equipment models manually. That is slow and error-prone. InfraLens treats OCR as an ingestion primitive for physical infrastructure: the challenge output remains simple and deterministic, while the product layer converts the same observation into a traceable asset record.

## Claim boundaries

- This is an experimental AMD AI Academy project.
- It does not claim official AMD endorsement.
- The Asset Passport parser is deterministic and intentionally conservative.
- OCR confidence reflects model inference, not a guarantee that every extracted identifier is correct.
