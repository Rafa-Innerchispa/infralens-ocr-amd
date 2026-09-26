"""Deterministic infrastructure Asset Passport extraction."""
from __future__ import annotations
import re
from typing import Any

BRANDS = [
    "Hikvision", "Dahua", "EZVIZ", "Ubiquiti", "UniFi", "ZKTeco",
    "Intelbras", "Grandstream", "TP-Link", "MikroTik", "Cisco", "APC",
    "Eaton", "Schneider Electric", "Huawei", "Dell", "HP", "Lenovo",
]
ASSET_HINTS = {
    "nvr": ("nvr", "network video recorder"),
    "camera": ("camera", "ip camera", "network camera"),
    "switch": ("switch", "poe switch"),
    "router": ("router", "gateway"),
    "access_point": ("access point", "wireless ap", "wifi ap"),
    "access_control": ("access control", "controller", "reader"),
    "inverter": ("inverter",),
    "ups": ("ups", "uninterruptible"),
    "breaker": ("breaker", "mcb", "rcbo"),
    "power_supply": ("power supply", "adapter"),
}
_PATTERNS = {
    "mac_addresses": re.compile(r"(?i)\b(?:[0-9A-F]{2}[:-]){5}[0-9A-F]{2}\b"),
    "ipv4_addresses": re.compile(
        r"(?<!\d)(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}"
        r"(?:25[0-5]|2[0-4]\d|1?\d?\d)(?!\d)"
    ),
    "serial_numbers": re.compile(
        r"(?im)\b(?:S/N|SN|SERIAL(?:\s+NO\.?|\s+NUMBER)?)[\s:#-]*"
        r"([A-Z0-9][A-Z0-9._/-]{3,})"
    ),
    "model_numbers": re.compile(
        r"(?im)\b(?:MODEL|MODEL\s+NO\.?|P/N|PART\s+NO\.?)"
        r"[\s:#-]*([A-Z0-9][A-Z0-9._/-]{2,})"
    ),
    "voltages": re.compile(r"(?i)\b\d{1,4}(?:\.\d+)?\s*V(?:AC|DC)?\b"),
    "currents": re.compile(r"(?i)\b\d{1,3}(?:\.\d+)?\s*A\b"),
    "power": re.compile(r"(?i)\b\d{1,5}(?:\.\d+)?\s*W\b"),
}

def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        key = value.upper()
        if key not in seen:
            seen.add(key)
            out.append(value)
    return out

def detect_brand(text: str) -> str | None:
    lower = text.lower()
    for brand in BRANDS:
        if brand.lower() in lower:
            return brand
    return None

def detect_asset_type(text: str) -> str:
    lower = text.lower()
    for asset_type, hints in ASSET_HINTS.items():
        if any(h in lower for h in hints):
            return asset_type
    return "unknown"

def build_asset_passport(text: str, confidence: float, runtime: dict[str, Any]) -> dict[str, Any]:
    entities: dict[str, list[str]] = {}
    for name, pattern in _PATTERNS.items():
        matches = pattern.findall(text)
        values = ["".join(x) if isinstance(x, tuple) else str(x) for x in matches]
        entities[name] = _unique([v.strip() for v in values if v.strip()])
    return {
        "schema": "infralens.asset-passport.v1",
        "asset_type": detect_asset_type(text),
        "brand": detect_brand(text),
        "ocr_confidence": round(float(confidence), 6),
        "raw_text": text,
        "entities": entities,
        "runtime": runtime,
    }
