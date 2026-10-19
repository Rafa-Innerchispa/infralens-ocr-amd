"""Structured visual-analysis helpers for the public InfraLens demo.

This module is presentation-side only. It does not change the Mini Challenge 2
grader contract. The model must fail soft when a field cannot be supported by
visible evidence.
"""
from __future__ import annotations

import json
import re
from typing import Any

VALID_TASKS = {"general", "asset", "text", "safety"}

SYSTEM_PROMPT = """You are InfraLens Vision running locally on AMD hardware.
Analyze only what is visibly supported by the image. Do not invent serials,
brands, model numbers, hazards, identities, locations, or hidden properties.
Return strict JSON only. Use null or an empty list when evidence is missing."""

TASK_PROMPTS = {
    "general": """Analyze this image as a field-inspection image.
Return JSON with exactly these keys:
{
  "summary": "one concise sentence",
  "object_type": "best visible category or unknown",
  "visible_text": ["verbatim visible text strings"],
  "identifiers": [{"kind": "serial|model|mac|ip|plate|other", "value": "..."}],
  "observations": ["short factual visible observations"],
  "warnings": ["visible caveats or uncertainty only"],
  "confidence": 0.0
}
confidence must be between 0 and 1.""",
    "asset": """Analyze this image as physical infrastructure or equipment.
Return JSON with exactly these keys:
{
  "summary": "one concise sentence",
  "object_type": "camera|nvr|switch|router|access_point|access_control|inverter|ups|breaker|power_supply|equipment|unknown",
  "brand": null,
  "model": null,
  "visible_text": ["verbatim visible text strings"],
  "identifiers": [{"kind": "serial|model|mac|ip|other", "value": "..."}],
  "observations": ["short factual visible observations"],
  "warnings": ["visible caveats or uncertainty only"],
  "confidence": 0.0
}
Never infer a brand/model that is not visibly supported.""",
    "text": """Read the visible text in the image and summarize what kind of
physical object or sign it appears on. Return JSON with exactly these keys:
{
  "summary": "one concise sentence",
  "object_type": "best visible category or unknown",
  "visible_text": ["verbatim text strings in reading order"],
  "identifiers": [],
  "observations": [],
  "warnings": [],
  "confidence": 0.0
}""",
    "safety": """Perform a non-authoritative visual field inspection.
Return only clearly visible conditions. Do not claim code compliance or
professional safety certification. Return JSON with exactly these keys:
{
  "summary": "one concise sentence",
  "object_type": "best visible category or unknown",
  "visible_text": ["verbatim visible text strings"],
  "identifiers": [],
  "observations": ["visible conditions only"],
  "warnings": ["possible visible concern, phrased as a review item"],
  "confidence": 0.0
}""",
}


def prompt_for_task(task: str) -> tuple[str, str]:
    task = (task or "general").strip().lower()
    if task not in VALID_TASKS:
        task = "general"
    return SYSTEM_PROMPT, TASK_PROMPTS[task]


def _extract_json(raw: str) -> dict[str, Any]:
    text = (raw or "").strip()
    if not text:
        raise ValueError("empty_analysis")
    try:
        value = json.loads(text)
        if isinstance(value, dict):
            return value
    except json.JSONDecodeError:
        pass

    fenced = re.search(r"\`\`\`(?:json)?\s*(\{.*?\})\s*\`\`\`", text, flags=re.S | re.I)
    if fenced:
        value = json.loads(fenced.group(1))
        if isinstance(value, dict):
            return value

    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        value = json.loads(text[start : end + 1])
        if isinstance(value, dict):
            return value
    raise ValueError("analysis_json_not_found")


def _string_list(value: Any, limit: int = 12) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value[:limit]:
        if isinstance(item, str) and item.strip():
            out.append(item.strip())
    return out


def normalize_analysis(raw: str, task: str) -> dict[str, Any]:
    payload = _extract_json(raw)
    confidence = payload.get("confidence", 0.0)
    try:
        confidence = max(0.0, min(1.0, float(confidence)))
    except (TypeError, ValueError):
        confidence = 0.0

    identifiers: list[dict[str, str]] = []
    for item in payload.get("identifiers", []) if isinstance(payload.get("identifiers"), list) else []:
        if not isinstance(item, dict):
            continue
        kind = str(item.get("kind") or "other").strip()[:40]
        value = str(item.get("value") or "").strip()[:200]
        if value:
            identifiers.append({"kind": kind, "value": value})

    result: dict[str, Any] = {
        "task": task if task in VALID_TASKS else "general",
        "summary": str(payload.get("summary") or "").strip()[:500],
        "object_type": str(payload.get("object_type") or "unknown").strip()[:120],
        "visible_text": _string_list(payload.get("visible_text")),
        "identifiers": identifiers[:16],
        "observations": _string_list(payload.get("observations")),
        "warnings": _string_list(payload.get("warnings")),
        "confidence": round(confidence, 4),
    }
    if "brand" in payload:
        result["brand"] = str(payload.get("brand") or "").strip()[:120] or None
    if "model" in payload:
        result["model"] = str(payload.get("model") or "").strip()[:160] or None
    return result
