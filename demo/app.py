from __future__ import annotations

import html
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
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root {
      --bg: #0a0f17;
      --panel: rgba(15, 23, 34, .82);
      --panel2: rgba(19, 31, 46, .78);
      --line: rgba(130, 166, 203, .18);
      --text: #f4f7fb;
      --muted: #9fb0c4;
      --cyan: #52d5ff;
      --blue: #5a7dff;
      --violet: #8b6cff;
      --green: #5de2b6;
    }

    .stApp {
      background:
        radial-gradient(circle at 12% 4%, rgba(82, 213, 255, .11), transparent 26rem),
        radial-gradient(circle at 92% 18%, rgba(139, 108, 255, .11), transparent 30rem),
        linear-gradient(180deg, #080d14 0%, #0b111b 55%, #091019 100%);
      color: var(--text);
    }

    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    #MainMenu, footer { visibility: hidden; }
    .block-container {
      max-width: 1380px;
      padding-top: 2.2rem;
      padding-bottom: 5rem;
    }

    .hero {
      position: relative;
      overflow: hidden;
      border: 1px solid rgba(111, 179, 233, .2);
      border-radius: 28px;
      padding: 42px 44px 38px;
      margin-bottom: 24px;
      background:
        linear-gradient(120deg, rgba(14, 25, 39, .97), rgba(14, 26, 42, .84) 55%, rgba(25, 20, 51, .78)),
        radial-gradient(circle at 80% 40%, rgba(82, 213, 255, .14), transparent 35%);
      box-shadow: 0 24px 70px rgba(0,0,0,.28);
    }

    .hero:before, .hero:after {
      content: "";
      position: absolute;
      pointer-events: none;
      border-radius: 999px;
      border: 1px solid rgba(82, 213, 255, .16);
    }
    .hero:before { width: 480px; height: 480px; right: -180px; top: -240px; }
    .hero:after { width: 300px; height: 300px; right: -60px; top: -110px; }

    .eyebrow {
      color: var(--cyan);
      letter-spacing: .16em;
      text-transform: uppercase;
      font-size: .78rem;
      font-weight: 700;
      margin-bottom: 12px;
    }

    .hero h1 {
      font-size: clamp(2.5rem, 5vw, 5rem);
      line-height: .98;
      margin: 0;
      max-width: 940px;
      letter-spacing: -.05em;
      color: #fff;
    }

    .hero .sub {
      max-width: 820px;
      font-size: 1.1rem;
      line-height: 1.65;
      color: var(--muted);
      margin: 20px 0 26px;
    }

    .chips { display:flex; flex-wrap:wrap; gap:10px; }
    .chip {
      padding: 8px 12px;
      border-radius: 999px;
      border: 1px solid rgba(111, 179, 233, .22);
      background: rgba(7, 16, 27, .58);
      color: #dce8f6;
      font-size: .84rem;
    }

    .story-grid {
      display:grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      margin: 18px 0 26px;
    }
    .story-card {
      min-height: 152px;
      border: 1px solid var(--line);
      border-radius: 20px;
      padding: 19px;
      background: linear-gradient(180deg, rgba(18,29,43,.84), rgba(11,19,29,.74));
    }
    .story-card .n {
      display:inline-flex;
      width:30px;
      height:30px;
      align-items:center;
      justify-content:center;
      border-radius:10px;
      background: linear-gradient(135deg, rgba(82,213,255,.19), rgba(139,108,255,.22));
      color: #cfefff;
      font-weight:800;
      margin-bottom:14px;
    }
    .story-card h3 { margin:0 0 7px; font-size:1rem; color:#fff; }
    .story-card p { margin:0; color:var(--muted); font-size:.88rem; line-height:1.5; }

    .section-title {
      margin: 30px 0 8px;
      font-size: 1.55rem;
      font-weight: 760;
      letter-spacing: -.025em;
    }
    .section-copy { color:var(--muted); margin-bottom:16px; }

    .mode-note {
      border: 1px solid var(--line);
      border-radius: 18px;
      background: rgba(15, 25, 38, .64);
      padding: 16px 18px;
      color: #c7d5e6;
      margin: 8px 0 18px;
    }

    .privacy {
      display:flex;
      align-items:center;
      gap:12px;
      border: 1px solid rgba(93, 226, 182, .18);
      background: rgba(24, 70, 62, .16);
      color:#c9efe3;
      border-radius:16px;
      padding:14px 16px;
      margin-top:14px;
    }
    .privacy-dot {
      width:9px;height:9px;border-radius:50%;
      background:var(--green);
      box-shadow:0 0 16px rgba(93,226,182,.7);
      flex:0 0 auto;
    }

    .result-head {
      border:1px solid var(--line);
      background:linear-gradient(120deg, rgba(16,29,43,.83), rgba(20,24,45,.77));
      border-radius:18px;
      padding:16px 18px;
      margin-bottom:16px;
    }
    .result-head strong { color:#fff; }
    .result-head span { color:var(--muted); }

    div[data-testid="stFileUploader"] {
      border: 1px dashed rgba(82, 213, 255, .34);
      border-radius: 22px;
      padding: 8px;
      background: rgba(9, 18, 29, .46);
    }
    div[data-testid="stMetric"] {
      background: rgba(15, 25, 38, .55);
      border: 1px solid var(--line);
      padding: 14px 16px;
      border-radius: 16px;
    }
    div[data-testid="stDataFrame"] { border-radius: 16px; overflow:hidden; }
    .stButton > button, .stDownloadButton > button {
      border-radius: 14px !important;
      border: 1px solid rgba(82,213,255,.25) !important;
    }

    @media (max-width: 900px) {
      .story-grid { grid-template-columns: 1fr 1fr; }
      .hero { padding: 28px 24px; }
    }
    @media (max-width: 560px) {
      .story-grid { grid-template-columns: 1fr; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

MODE_COPY = {
    "Challenge OCR": (
        "Read difficult plates and road signs exactly as the challenge requires. "
        "The result shows recognized text, confidence and runtime evidence."
    ),
    "Asset Passport": (
        "Turn a photographed equipment label into a structured physical-asset record: "
        "device type, brand and identifiers such as serial, MAC/IP or electrical data."
    ),
    "Batch Intake": (
        "Process several field photos in one intake and transform them into an inventory preview "
        "instead of manually typing equipment records."
    ),
}

def call_ocr(data: bytes) -> dict[str, Any]:
    req = urllib.request.Request(
        OCR_URL,
        data=data,
        headers={"Content-Type": "application/octet-stream"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=35) as response:
        return json.loads(response.read().decode("utf-8"))


def safe(value: Any) -> str:
    return html.escape(str(value if value not in (None, "") else "—"))


def render_hero() -> None:
    st.markdown(
        """
        <section class="hero">
          <div class="eyebrow">AMD ROCm · local-first physical intelligence</div>
          <h1>See infrastructure.<br/>Understand the asset.</h1>
          <p class="sub">
            InfraLens turns real-world photos into usable infrastructure data.
            It reads difficult visual text locally on AMD, identifies what the equipment is,
            and converts the result into a structured Asset Passport that can feed inventory,
            field operations and automation.
          </p>
          <div class="chips">
            <span class="chip">Radeon AI PRO R9700</span>
            <span class="chip">ROCm inference</span>
            <span class="chip">No external vision API</span>
            <span class="chip">OCR → Asset Passport</span>
            <span class="chip">FieldOps ready</span>
          </div>
        </section>

        <div class="story-grid">
          <div class="story-card">
            <div class="n">01</div>
            <h3>Capture</h3>
            <p>Drop a plate, road sign or equipment label from the real physical environment.</p>
          </div>
          <div class="story-card">
            <div class="n">02</div>
            <h3>Read on AMD</h3>
            <p>ROCm-powered local inference extracts difficult visual text without sending the image to an external API.</p>
          </div>
          <div class="story-card">
            <div class="n">03</div>
            <h3>Understand</h3>
            <p>InfraLens turns raw OCR into device type, brand and structured identifiers.</p>
          </div>
          <div class="story-card">
            <div class="n">04</div>
            <h3>Act</h3>
            <p>The Asset Passport becomes usable inventory data for field service, audits and automation.</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_result(name: str, data: bytes, result: dict[str, Any], mode: str) -> None:
    confidence = float(result.get("confidence", 0.0))
    passport = result.get("asset_passport") or {}

    st.markdown(
        f"""
        <div class="result-head">
          <strong>Scan complete</strong><br/>
          <span>{safe(name)} · local AMD inference · structured result ready</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.08, 1], gap="large")
    with left:
        st.image(Image.open(io.BytesIO(data)), caption=name, use_container_width=True)

    with right:
        m1, m2 = st.columns(2)
        m1.metric("OCR confidence", f"{confidence * 100:.1f}%")
        m2.metric("Processing", "Local AMD")

        st.markdown("#### Recognized text")
        st.code(result.get("text", "") or "(empty)", language=None)

        if mode != "Challenge OCR":
            st.markdown("#### Asset Passport")
            meta1, meta2 = st.columns(2)
            meta1.metric("Asset type", passport.get("asset_type", "unknown"))
            meta2.metric("Brand", passport.get("brand") or "unknown")

            entities = passport.get("entities") or {}
            rows = []
            for kind, values in entities.items():
                for value in values or []:
                    rows.append({"Field": kind, "Detected value": value})
            if rows:
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                st.info("No structured infrastructure identifiers were detected in this image.")

            st.download_button(
                "Download Asset Passport JSON",
                data=json.dumps(passport, ensure_ascii=False, indent=2),
                file_name=f"{name.rsplit('.', 1)[0]}_asset_passport.json",
                mime="application/json",
                use_container_width=True,
            )

        with st.expander("AMD runtime evidence"):
            st.caption(
                "Challenge evidence stays separate from the presentation layer. "
                "This panel exposes the runtime metadata returned by the local OCR service."
            )
            st.json(
                {
                    "info": result.get("info", {}),
                    "runtime": passport.get("runtime", {}),
                }
            )


render_hero()

st.markdown('<div class="section-title">Choose the field workflow</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-copy">One engine, three ways to turn pixels into operational data.</div>',
    unsafe_allow_html=True,
)

mode = st.radio(
    "Mode",
    ["Challenge OCR", "Asset Passport", "Batch Intake"],
    horizontal=True,
    label_visibility="collapsed",
)

st.markdown(
    f'<div class="mode-note"><strong>{safe(mode)}</strong><br>{safe(MODE_COPY[mode])}</div>',
    unsafe_allow_html=True,
)

multiple = mode == "Batch Intake"
uploads = st.file_uploader(
    "Drop a plate, road sign, equipment label, NVR, switch, router, access controller or inverter photo",
    type=["png", "jpg", "jpeg", "webp", "tif", "tiff"],
    accept_multiple_files=multiple,
)

st.markdown(
    """
    <div class="privacy">
      <span class="privacy-dot"></span>
      <div><strong>Private by design.</strong> The image is processed by the local InfraLens OCR service on AMD hardware. No external vision API receives the image.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if uploads:
    items = uploads if isinstance(uploads, list) else [uploads]
    results = []

    with st.status("Analyzing physical-world input on AMD…", expanded=False) as status:
        for upload in items:
            data = upload.getvalue()
            try:
                result = call_ocr(data)
                results.append((upload.name, data, result))
            except Exception as exc:
                st.error(f"{upload.name}: {type(exc).__name__}: {exc}")
        if results:
            status.update(label=f"{len(results)} scan(s) completed", state="complete")
        else:
            status.update(label="No scan completed", state="error")

    if mode == "Batch Intake" and results:
        st.markdown('<div class="section-title">Batch inventory preview</div>', unsafe_allow_html=True)
        st.caption("Each image becomes a candidate asset record instead of a manual spreadsheet row.")
        summary = []
        for name, _data, result in results:
            passport = result.get("asset_passport") or {}
            summary.append(
                {
                    "File": name,
                    "Recognized text": result.get("text", ""),
                    "Confidence": f"{float(result.get('confidence', 0.0)) * 100:.1f}%",
                    "Asset type": passport.get("asset_type", "unknown"),
                    "Brand": passport.get("brand") or "",
                }
            )
        st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)

    for name, data, result in results:
        st.divider()
        render_result(name, data, result, mode)
else:
    st.markdown(
        """
        <div class="section-title">Try it with something real</div>
        <div class="section-copy">
          A road sign proves the OCR challenge. An NVR, switch, router, access controller or inverter label shows the product idea:
          the same visual intelligence becomes a reusable Asset Passport.
        </div>
        """,
        unsafe_allow_html=True,
    )
