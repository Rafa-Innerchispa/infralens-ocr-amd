#!/usr/bin/env python3
"""Generate deterministic E2E fixture images for Track 2 validation."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "e2e"


def _font(size: int = 28) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def save_plate(path: Path) -> None:
    img = Image.new("RGB", (640, 180), "#f4f4f4")
    draw = ImageDraw.Draw(img)
    draw.rectangle((20, 30, 620, 150), outline="#222", width=4)
    draw.text((180, 70), "ABC1234", fill="#111", font=_font(48))
    img.save(path)


def save_nvr_label(path: Path) -> None:
    img = Image.new("RGB", (720, 420), "white")
    draw = ImageDraw.Draw(img)
    font = _font(24)
    lines = [
        "Hikvision Network Video Recorder",
        "MODEL: DS-7608NI-K2",
        "S/N: E12345678",
        "MAC: AA:BB:CC:DD:EE:FF",
        "IP: 192.168.1.64",
        "12V DC 2A",
    ]
    y = 40
    for line in lines:
        draw.text((40, y), line, fill="black", font=font)
        y += 52
    img.save(path)


def save_sign(path: Path) -> None:
    img = Image.new("RGB", (480, 360), "#1a5f2a")
    draw = ImageDraw.Draw(img)
    draw.text((90, 140), "STOP", fill="white", font=_font(56))
    img.save(path)


def main() -> None:
    FIXTURES.mkdir(parents=True, exist_ok=True)
    save_plate(FIXTURES / "challenge_plate.png")
    save_nvr_label(FIXTURES / "asset_nvr_label.png")
    save_sign(FIXTURES / "batch_sign.png")
    print(f"Wrote fixtures under {FIXTURES}")


if __name__ == "__main__":
    main()
