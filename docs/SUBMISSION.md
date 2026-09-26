# Lablab Submission Copy — Mini Challenge 2

## Title

InfraLens OCR: Physical Assets to Data

## Long description

InfraLens OCR turns photos of real infrastructure into machine-readable data on AMD ROCm. The Mini Challenge 2 core follows the grader contract exactly: a Docker container based on the mandated AMD ROCm/PyTorch image loads its OCR model once, accepts an input image through the required CLI, and writes a JSON result containing only the recognized text and confidence.

I extended that core into something I can use after the challenge. InfraLens can photograph an NVR, security camera, network switch, access-control panel, router, inverter, breaker label or equipment plate and create an additional Asset Passport. The passport deterministically extracts fields such as brand, model, serial number, MAC address, IP address and electrical ratings while preserving the original OCR text as evidence.

The OCR path uses PyTorch on AMD ROCm with TrOCR and lightweight OpenCV preprocessing/line segmentation. Model weights are baked into the image so container startup does not depend on an external model download. A small local daemon loads the model once and serves repeated image requests within the challenge time budget.

The project is designed as a reusable ingestion module for field-service and physical-infrastructure systems such as inventory, maintenance and AI-assisted building operations, rather than a one-off OCR screenshot.

## Suggested categories

- Computer Vision
- Developer Tools
- Productivity

## Technologies

- AMD ROCm
- PyTorch
- Hugging Face
- OpenCV
- Docker
- TrOCR

## One-line pitch

Point a camera at physical infrastructure. Get trusted OCR plus a machine-readable Asset Passport.
