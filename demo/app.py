from __future__ import annotations

import io
import json
import os
import urllib.request
from typing import Any

import pandas as pd
import streamlit as st
from PIL import Image

OCR_URL = os.getenv("INFRALENS_OCR_URL", "http://127.0.0.1:8765/ocr")

st.set_page_config(
    page_title="InfraLens Field Scanner",
    page_icon="🔎",
    layout="wide",
)

st.title("InfraLens Field Scanner")
st.caption("AMD ROCm OCR + Asset Passport for physical infrastructure")

mode = st.radio(
    "Mode",
    ["Challenge OCR", "Asset Passport", "Batch Intake"],
    horizontal=True,
)

def call_ocr(data: bytes) -> dict[str, Any]:
    req = urllib.request.Request(
        OCR_URL,
        data=data,
        headers={"Content-Type": "application/octet-stream"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=35) as response:
        return json.loads(response.read().decode("utf-8"))

def render_result(name: str, data: bytes, result: dict[str, Any]) -> None:
    left, right = st.columns([1, 1])
    with left:
        st.image(Image.open(io.BytesIO(data)), caption=name, use_container_width=True)
    with right:
        confidence = float(result.get("confidence", 0.0))
        st.metric("OCR confidence", f"{confidence * 100:.1f}%")
        st.subheader("Recognized text")
        st.code(result.get("text", "") or "(empty)", language=None)

        if mode != "Challenge OCR":
            passport = result.get("asset_passport") or {}
            st.subheader("Asset Passport")
            meta1, meta2 = st.columns(2)
            meta1.metric("Asset type", passport.get("asset_type", "unknown"))
            meta2.metric("Brand", passport.get("brand") or "unknown")
            entities = passport.get("entities") or {}
            rows = []
            for kind, values in entities.items():
                for value in values or []:
                    rows.append({"field": kind, "value": value})
            if rows:
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                st.info("No structured infrastructure identifiers detected.")
            st.download_button(
                "Download Asset Passport JSON",
                data=json.dumps(passport, ensure_ascii=False, indent=2),
                file_name=f"{name.rsplit('.', 1)[0]}_asset_passport.json",
                mime="application/json",
            )

        with st.expander("Runtime evidence"):
            st.json({
                "info": result.get("info", {}),
                "runtime": (result.get("asset_passport") or {}).get("runtime", {}),
            })

multiple = mode == "Batch Intake"
uploads = st.file_uploader(
    "Drop a plate, road sign, equipment label, NVR, switch, router, access controller or inverter photo",
    type=["png", "jpg", "jpeg", "webp", "tif", "tiff"],
    accept_multiple_files=multiple,
)

if uploads:
    items = uploads if isinstance(uploads, list) else [uploads]
    results = []
    for upload in items:
        data = upload.getvalue()
        try:
            result = call_ocr(data)
            results.append((upload.name, data, result))
        except Exception as exc:
            st.error(f"{upload.name}: {type(exc).__name__}: {exc}")

    if mode == "Batch Intake" and results:
        summary = []
        for name, _data, result in results:
            passport = result.get("asset_passport") or {}
            summary.append({
                "file": name,
                "text": result.get("text", ""),
                "confidence": result.get("confidence", 0.0),
                "asset_type": passport.get("asset_type", "unknown"),
                "brand": passport.get("brand") or "",
            })
        st.subheader("Batch inventory preview")
        st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)

    for name, data, result in results:
        st.divider()
        render_result(name, data, result)
else:
    st.info(
        "The UI talks only to the local InfraLens OCR service. "
        "No image is sent to an external API."
    )
