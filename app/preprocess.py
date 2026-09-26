"""Image enhancement and text-line segmentation."""
from __future__ import annotations
from dataclasses import dataclass
from PIL import Image, ImageEnhance, ImageOps

@dataclass(frozen=True)
class Region:
    box: tuple[int, int, int, int]
    image: Image.Image

def enhance(image: Image.Image) -> Image.Image:
    image = ImageOps.exif_transpose(image).convert("RGB")
    image = ImageOps.autocontrast(image, cutoff=0.5)
    return ImageEnhance.Sharpness(image).enhance(1.25)

def load_image(path: str) -> Image.Image:
    with Image.open(path) as image:
        return enhance(image.copy())

def _merge_lines(boxes: list[tuple[int, int, int, int]]) -> list[tuple[int, int, int, int]]:
    boxes = sorted(boxes, key=lambda b: (b[1], b[0]))
    merged: list[list[int]] = []
    for x1, y1, x2, y2 in boxes:
        cy = (y1 + y2) / 2
        placed = False
        for current in merged:
            ccy = (current[1] + current[3]) / 2
            ch = max(1, current[3] - current[1])
            h = max(1, y2 - y1)
            if abs(cy - ccy) <= 0.6 * max(ch, h):
                current[0] = min(current[0], x1)
                current[1] = min(current[1], y1)
                current[2] = max(current[2], x2)
                current[3] = max(current[3], y2)
                placed = True
                break
        if not placed:
            merged.append([x1, y1, x2, y2])
    return [tuple(b) for b in merged]

def segment_text_lines(image: Image.Image, max_regions: int = 5) -> list[Region]:
    # OpenCV/Numpy are intentionally imported lazily. Contract tests using the
    # stub backend do not need the heavy OCR runtime.
    import cv2
    import numpy as np

    arr = np.asarray(image)
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
    grad = cv2.morphologyEx(
        clahe, cv2.MORPH_GRADIENT, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    )
    _, bw = cv2.threshold(grad, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kx = max(9, min(35, image.width // 40))
    closed = cv2.morphologyEx(
        bw, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (kx, 3))
    )
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes: list[tuple[int, int, int, int]] = []
    min_area = max(120, (image.width * image.height) // 3000)
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w * h < min_area or w < 24 or h < 8 or w / max(h, 1) < 1.2:
            continue
        pad_x = max(4, int(w * 0.04))
        pad_y = max(4, int(h * 0.25))
        boxes.append((
            max(0, x - pad_x), max(0, y - pad_y),
            min(image.width, x + w + pad_x), min(image.height, y + h + pad_y)
        ))
    boxes = sorted(_merge_lines(boxes), key=lambda b: (b[1], b[0]))
    if not boxes or len(boxes) > max_regions:
        boxes = [(0, 0, image.width, image.height)]
    regions: list[Region] = []
    for box in boxes[:max_regions]:
        crop = image.crop(box)
        if crop.height < 64:
            scale = 64 / max(crop.height, 1)
            crop = crop.resize((max(64, int(crop.width * scale)), 64), Image.Resampling.LANCZOS)
        regions.append(Region(box=box, image=crop))
    return regions
