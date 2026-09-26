"""Public Mini Challenge 2 normalization rules for InfraLens."""
from __future__ import annotations
import re

SYSTEM_PROMPT = (
    "You are a strict OCR engine. Read printed characters from the image. "
    "Do not describe the image and do not explain your answer."
)

USER_PROMPT = """Return ONLY the text that should be graded, on one line.

Rules:
- License plate: output only the registration. Drop state/country names, slogans,
  mottos, county names, dealer frames, stickers and URLs around it.
- Mainland Chinese plate: keep the leading province character and following letter.
  In the serial part interpret printed I/O as 1/0.
- Road sign: output visible words and numbers in reading order, top to bottom.
- Numeric advisory plaque: if the image prints only a number, return only that number.
  Never invent MPH, km/h or another unit.
- If SPEED LIMIT or other words are visibly printed, keep them.
- Vanity plate: preserve its registration text even when it spells ordinary words.
- Other technical label/document: transcribe all clearly visible text in reading order.
- No OCR labels, quotes, markdown or commentary."""

STATES = [
    "ALABAMA","ALASKA","ARIZONA","ARKANSAS","CALIFORNIA","COLORADO",
    "CONNECTICUT","DELAWARE","FLORIDA","GEORGIA","HAWAII","IDAHO",
    "ILLINOIS","INDIANA","IOWA","KANSAS","KENTUCKY","LOUISIANA",
    "MAINE","MARYLAND","MASSACHUSETTS","MICHIGAN","MINNESOTA",
    "MISSISSIPPI","MISSOURI","MONTANA","NEBRASKA","NEVADA",
    "NEW HAMPSHIRE","NEW JERSEY","NEW MEXICO","NEW YORK",
    "NORTH CAROLINA","NORTH DAKOTA","OHIO","OKLAHOMA","OREGON",
    "PENNSYLVANIA","RHODE ISLAND","SOUTH CAROLINA","SOUTH DAKOTA",
    "TENNESSEE","TEXAS","UTAH","VERMONT","VIRGINIA","WASHINGTON",
    "WEST VIRGINIA","WISCONSIN","WYOMING","DISTRICT OF COLUMBIA",
]
NOISE = [
    "EMPIRE STATE","LONE STAR STATE","SUNSHINE STATE","GARDEN STATE",
    "LAND OF LINCOLN","FIRST IN FLIGHT","LIVE FREE OR DIE",
    "FAMOUS POTATOES","VACATIONLAND","AMERICA'S DAIRYLAND",
    "GRAND CANYON STATE","THE SILVER STATE","GOLDEN STATE",
    "IN GOD WE TRUST","MYFLORIDA.COM","DMV.CA.GOV",
]
PREFIX_RE = re.compile(
    r"^(?:OCR|TEXT|ANSWER|OUTPUT|RESULT|PLATE|LICENSE\s+PLATE|"
    r"REGISTRATION(?:\s+NUMBER)?|SIGN|TRANSCRIPTION)\s*(?:IS|:|-)*\s*",
    re.I,
)
URL_RE = re.compile(r"(?i)\b(?:www\.)?[a-z0-9-]+(?:\.[a-z0-9-]+)+\b")
CN_RE = re.compile(r"^([\u4e00-\u9fff])\s*([A-Z])\s*[·.\-_ ]*([A-Z0-9·.\-_ ]{4,8})$")

def vote_key(text: str) -> str:
    return re.sub(r"[\s\-._·]", "", (text or "").upper())

def _strip_plate_context(text: str) -> str:
    original = text
    cleaned = URL_RE.sub(" ", text)
    for phrase in sorted(STATES + NOISE, key=len, reverse=True):
        cleaned = re.sub(
            rf"(?i)(?<![A-Z0-9]){re.escape(phrase)}(?![A-Z0-9])",
            " ",
            cleaned,
        )
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" -.,:;")
    compact = vote_key(cleaned)
    if 2 <= len(compact) <= 10 and re.search(r"[A-Z0-9\u4e00-\u9fff]", compact):
        return cleaned
    return original

def _fix_cn(text: str) -> str:
    match = CN_RE.match(text.upper().strip())
    if not match:
        return text
    province, letter, serial = match.groups()
    serial = re.sub(r"[\s·.\-_]", "", serial).replace("I", "1").replace("O", "0")
    return f"{province}{letter}{serial}"

def clean_text(raw: str) -> str:
    lines = [line.strip() for line in (raw or "").splitlines() if line.strip()]
    if not lines:
        return ""
    text = " ".join(lines).replace("**", "")
    text = PREFIX_RE.sub("", text)
    text = re.sub(r"\s+", " ", text).strip(" \t\r\n\"'“”‘’.:;,")
    text = _fix_cn(_strip_plate_context(text))
    numeric_unit = re.fullmatch(r"(\d{1,3})\s*(?:MPH|KM/?H|KPH)", text, flags=re.I)
    return numeric_unit.group(1) if numeric_unit else text
