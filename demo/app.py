from __future__ import annotations

import base64
import html
import io
import json
import os
import urllib.request
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
from PIL import Image

OCR_URL = os.getenv("INFRALENS_OCR_URL", "http://127.0.0.1:8765/ocr")
ANALYZE_URL = os.getenv("INFRALENS_ANALYZE_URL", OCR_URL.rsplit("/ocr", 1)[0] + "/analyze")

VISION_MODEL = "Qwen/Qwen2.5-VL-3B-Instruct"
REASONING_MODEL = "QuantTrio/Qwen3-Coder-30B-A3B-Instruct-AWQ"
HERO_BG = ""
try:
    HERO_BG = (Path(__file__).with_name("hero_bg.b64")).read_text(encoding="utf-8").strip()
except Exception:
    HERO_BG = ""

st.set_page_config(
    page_title="InfraLens Field Scanner",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

hero_image_css = (
    f"url('data:image/webp;base64,{HERO_BG}')"
    if HERO_BG
    else "linear-gradient(135deg,#0d1723,#15203a)"
)

st.markdown(
    f"""
    <style>
    :root {{
      --bg: #070c13;
      --panel: rgba(13, 22, 34, .82);
      --panel-strong: rgba(11, 19, 31, .94);
      --line: rgba(120, 174, 225, .20);
      --text: #f7f9fc;
      --muted: #9eb0c5;
      --cyan: #45d7ff;
      --blue: #5a7dff;
      --violet: #9b61ff;
      --green: #50e3ae;
      --red: #ff5d67;
    }}

    .stApp {{
      background:
        radial-gradient(circle at 8% 0%, rgba(45, 190, 255, .10), transparent 28rem),
        radial-gradient(circle at 88% 18%, rgba(123, 82, 255, .12), transparent 32rem),
        linear-gradient(180deg, #070b12 0%, #0b111a 55%, #071019 100%);
      color: var(--text);
    }}

    [data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}
    #MainMenu, footer {{ visibility: hidden; }}
    .block-container {{
      max-width: 1460px;
      padding-top: 1.4rem;
      padding-bottom: 5rem;
    }}

    .topbar {{
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap:18px;
      margin: 2px 0 14px;
      padding: 4px 4px;
    }}
    .brand {{
      display:flex;
      align-items:center;
      gap:12px;
      font-size:1.1rem;
      color:#dce8f5;
    }}
    .brand-mark {{
      width:34px;height:34px;border-radius:10px;
      border:1px solid rgba(69,215,255,.45);
      display:flex;align-items:center;justify-content:center;
      color:var(--cyan);
      box-shadow:0 0 24px rgba(69,215,255,.15);
      font-weight:900;
    }}
    .powered {{
      border:1px solid rgba(120,174,225,.26);
      background:rgba(8,15,25,.68);
      border-radius:13px;
      padding:9px 13px;
      color:#c9d7e7;
      font-size:.82rem;
    }}
    .powered b {{ color:white; letter-spacing:.08em; }}

    .hero {{
      position:relative;
      min-height:520px;
      overflow:hidden;
      border:1px solid rgba(111,179,233,.22);
      border-radius:30px;
      padding:48px 48px 44px;
      margin-bottom:22px;
      background-image:
        linear-gradient(90deg, rgba(5,11,18,.98) 0%, rgba(7,15,25,.92) 43%, rgba(8,13,24,.48) 72%, rgba(9,12,22,.58) 100%),
        {hero_image_css};
      background-size:cover;
      background-position:center;
      box-shadow:0 26px 80px rgba(0,0,0,.34);
    }}
    .hero:after {{
      content:"";
      position:absolute;inset:0;
      background:
        linear-gradient(90deg, transparent 0 72%, rgba(69,215,255,.04) 72% 72.2%, transparent 72.2%),
        linear-gradient(180deg, transparent 0 72%, rgba(155,97,255,.05) 72% 72.2%, transparent 72.2%);
      pointer-events:none;
    }}
    .hero-copy {{ position:relative; z-index:2; max-width:770px; }}
    .eyebrow {{
      color:var(--cyan);
      letter-spacing:.16em;
      text-transform:uppercase;
      font-size:.76rem;
      font-weight:800;
      margin-bottom:14px;
    }}
    .hero h1 {{
      font-size:clamp(2.9rem, 5.5vw, 5.6rem);
      line-height:.94;
      margin:0;
      letter-spacing:-.055em;
      color:#fff;
      text-wrap:balance;
    }}
    .gradient {{
      background:linear-gradient(90deg,var(--cyan),#7a8dff 55%,#c45cff);
      -webkit-background-clip:text;
      background-clip:text;
      color:transparent;
    }}
    .hero .sub {{
      max-width:710px;
      color:#bac8d8;
      font-size:1.07rem;
      line-height:1.66;
      margin:22px 0 24px;
    }}
    .chips {{ display:flex;flex-wrap:wrap;gap:9px; }}
    .chip {{
      padding:8px 11px;
      border-radius:999px;
      border:1px solid rgba(120,174,225,.24);
      background:rgba(5,12,21,.70);
      color:#d9e6f4;
      font-size:.82rem;
      backdrop-filter:blur(8px);
    }}

    .story-grid {{
      display:grid;
      grid-template-columns:repeat(4,1fr);
      gap:12px;
      margin:16px 0 28px;
    }}
    .story-card {{
      min-height:145px;
      border:1px solid var(--line);
      border-radius:19px;
      padding:18px;
      background:linear-gradient(180deg,rgba(18,29,43,.86),rgba(9,17,27,.78));
    }}
    .story-card .n {{
      display:inline-flex;width:30px;height:30px;align-items:center;justify-content:center;
      border-radius:9px;background:linear-gradient(135deg,rgba(69,215,255,.18),rgba(155,97,255,.22));
      color:#d8f6ff;font-weight:800;margin-bottom:12px;
    }}
    .story-card h3 {{ margin:0 0 6px;font-size:1rem;color:white; }}
    .story-card p {{ margin:0;color:var(--muted);font-size:.86rem;line-height:1.48; }}

    .section-title {{
      margin:30px 0 7px;
      font-size:1.5rem;
      font-weight:780;
      letter-spacing:-.025em;
    }}
    .section-copy {{ color:var(--muted); margin-bottom:15px; }}

    .stack {{
      display:grid;
      grid-template-columns:1fr 1fr 1fr 1fr;
      gap:10px;
      margin:14px 0 22px;
    }}
    .stack-card {{
      border:1px solid var(--line);
      border-radius:16px;
      background:rgba(12,21,33,.72);
      padding:14px 15px;
    }}
    .stack-card .label {{
      color:#7f93aa;font-size:.72rem;text-transform:uppercase;letter-spacing:.09em;margin-bottom:5px;
    }}
    .stack-card .value {{ color:white;font-size:.9rem;font-weight:700; }}
    .stack-card .small {{ color:var(--muted);font-size:.76rem;margin-top:4px;line-height:1.35; }}

    .privacy {{
      display:flex;align-items:center;gap:11px;
      border:1px solid rgba(80,227,174,.20);
      background:rgba(24,70,62,.15);
      color:#c9efe3;border-radius:15px;padding:13px 15px;margin:12px 0 4px;
    }}
    .privacy-dot {{
      width:9px;height:9px;border-radius:50%;background:var(--green);
      box-shadow:0 0 16px rgba(80,227,174,.75);flex:0 0 auto;
    }}

    .scan-frame {{
      position:relative;
      border:1px solid rgba(69,215,255,.33);
      border-radius:20px;
      overflow:hidden;
      background:#071019;
      box-shadow:inset 0 0 40px rgba(69,215,255,.04),0 0 35px rgba(75,95,255,.09);
    }}
    .scan-frame img {{ width:100%;display:block;max-height:570px;object-fit:contain;background:#060b11; }}
    .scan-line {{
      position:absolute;left:3%;right:3%;height:2px;top:8%;
      background:linear-gradient(90deg,transparent,var(--cyan),#b36cff,transparent);
      box-shadow:0 0 18px rgba(69,215,255,.8);
      animation:scan 3.4s ease-in-out infinite;
      opacity:.92;
    }}
    @keyframes scan {{
      0%,100% {{ top:8%; opacity:.45; }}
      50% {{ top:91%; opacity:1; }}
    }}
    .corner {{
      position:absolute;width:30px;height:30px;border-color:var(--cyan);opacity:.85;
    }}
    .tl {{top:10px;left:10px;border-top:2px solid;border-left:2px solid}}
    .tr {{top:10px;right:10px;border-top:2px solid;border-right:2px solid}}
    .bl {{bottom:10px;left:10px;border-bottom:2px solid;border-left:2px solid}}
    .br {{bottom:10px;right:10px;border-bottom:2px solid;border-right:2px solid}}

    .result-head {{
      border:1px solid var(--line);
      background:linear-gradient(120deg,rgba(16,29,43,.86),rgba(20,24,45,.80));
      border-radius:17px;padding:15px 17px;margin-bottom:15px;
    }}
    .result-head strong {{ color:white; }}
    .result-head span {{ color:var(--muted); }}

    .observation {{
      border:1px solid rgba(120,174,225,.18);
      background:rgba(12,22,34,.62);
      border-radius:13px;
      padding:10px 12px;
      margin:6px 0;
      color:#d8e4f2;
    }}
    .warning {{
      border-color:rgba(255,160,90,.24);
      background:rgba(90,48,20,.18);
      color:#ffd7b8;
    }}

    div[data-testid="stFileUploader"], div[data-testid="stCameraInput"] {{
      border:1px dashed rgba(69,215,255,.30);
      border-radius:20px;padding:7px;background:rgba(7,16,27,.44);
    }}
    div[data-testid="stMetric"] {{
      background:rgba(15,25,38,.56);
      border:1px solid var(--line);
      padding:13px 15px;border-radius:15px;
    }}
    .stButton > button, .stDownloadButton > button {{
      border-radius:13px !important;
      border:1px solid rgba(69,215,255,.24) !important;
    }}

    @media (max-width:950px) {{
      .story-grid,.stack {{ grid-template-columns:1fr 1fr; }}
      .hero {{ min-height:460px;padding:34px 26px; }}
    }}
    @media (max-width:590px) {{
      .story-grid,.stack {{ grid-template-columns:1fr; }}
      .hero {{ min-height:520px; }}
      .topbar {{ align-items:flex-start; }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

ANALYSIS_MODES = {
    "Challenge OCR": {
        "task": "ocr",
        "copy": "Read difficult plates and road signs exactly as Mini Challenge 2 requires.",
    },
    "Identify an asset": {
        "task": "asset",
        "copy": "Identify visible infrastructure, labels and identifiers, then create an Asset Passport.",
    },
    "General visual analysis": {
        "task": "general",
        "copy": "Ask the resident vision model what is visibly present, with evidence-first structured output.",
    },
    "Visual field inspection": {
        "task": "safety",
        "copy": "Surface visible conditions and review items without pretending to replace a professional inspection.",
    },
}


def safe(value: Any) -> str:
    return html.escape(str(value if value not in (None, "") else "—"))


def image_data_uri(data: bytes) -> str:
    with Image.open(io.BytesIO(data)) as source:
        image = source.convert("RGB")
    output = io.BytesIO()
    image.thumbnail((1600, 1200), Image.Resampling.LANCZOS)
    image.save(output, format="JPEG", quality=88, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(output.getvalue()).decode("ascii")


def post_image(url: str, data: bytes, headers: dict[str, str] | None = None) -> dict[str, Any]:
    request_headers = {"Content-Type": "application/octet-stream"}
    request_headers.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=request_headers, method="POST")
    with urllib.request.urlopen(req, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))


def call_ocr(data: bytes) -> dict[str, Any]:
    return post_image(OCR_URL, data)


def call_analysis(data: bytes, task: str) -> dict[str, Any]:
    return post_image(ANALYZE_URL, data, {"X-InfraLens-Task": task})


def render_top() -> None:
    st.markdown(
        """
        <div class="topbar">
          <div class="brand"><div class="brand-mark">◈</div><div><b>InfraLens</b> &nbsp;Field Scanner</div></div>
          <div class="powered">Powered by <b>AMD</b> · Radeon AI PRO R9700 · ROCm</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <section class="hero">
          <div class="hero-copy">
            <div class="eyebrow">Infrastructure → Vision → Intelligence</div>
            <h1>See infrastructure.<br/><span class="gradient">Understand the asset.</span></h1>
            <p class="sub">
              Capture a photo from the device camera or upload one. InfraLens processes it on our AMD R9700,
              reads visible text, understands the physical object, and turns supported evidence into structured
              operational data.
            </p>
            <div class="chips">
              <span class="chip">Live device camera</span>
              <span class="chip">Qwen2.5-VL vision</span>
              <span class="chip">Local AMD inference</span>
              <span class="chip">No external vision API</span>
              <span class="chip">Asset Passport</span>
            </div>
          </div>
        </section>
        <div class="story-grid">
          <div class="story-card"><div class="n">01</div><h3>Capture</h3><p>Use the browser camera, USB/webcam exposed by the browser, or upload a field photo.</p></div>
          <div class="story-card"><div class="n">02</div><h3>See on AMD</h3><p>Qwen2.5-VL analyzes the pixels locally on the Radeon AI PRO R9700.</p></div>
          <div class="story-card"><div class="n">03</div><h3>Understand</h3><p>Choose OCR, asset identification, general visual analysis, or a field-inspection view.</p></div>
          <div class="story-card"><div class="n">04</div><h3>Act</h3><p>Export the structured result or Asset Passport for inventory, FieldOps and automation.</p></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stack(runtime: dict[str, Any] | None = None) -> None:
    runtime = runtime or {}
    gpu = runtime.get("gpu_name") or "AMD Radeon AI PRO R9700"
    hip = runtime.get("hip") or "ROCm"
    st.markdown(
        f"""
        <div class="stack">
          <div class="stack-card"><div class="label">Vision model</div><div class="value">Qwen2.5-VL-3B-Instruct</div><div class="small">Sees the image, reads text and produces structured visual evidence.</div></div>
          <div class="stack-card"><div class="label">GPU</div><div class="value">{safe(gpu)}</div><div class="small">Physical AMD 1.5 inference host.</div></div>
          <div class="stack-card"><div class="label">ROCm / HIP</div><div class="value">{safe(hip)}</div><div class="small">AMD acceleration layer used by the visual model.</div></div>
          <div class="stack-card"><div class="label">Resident reasoning</div><div class="value">Qwen3-Coder 30B</div><div class="small">Available on the same host for text reasoning. It is not used to pretend it can see pixels.</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_scan_image(data: bytes, name: str) -> None:
    uri = image_data_uri(data)
    st.markdown(
        f"""
        <div class="scan-frame">
          <img src="{uri}" alt="{safe(name)}"/>
          <div class="scan-line"></div>
          <div class="corner tl"></div><div class="corner tr"></div>
          <div class="corner bl"></div><div class="corner br"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_passport(passport: dict[str, Any], name: str) -> None:
    st.markdown("#### Asset Passport")
    c1, c2 = st.columns(2)
    c1.metric("Asset type", passport.get("asset_type", "unknown"))
    c2.metric("Brand", passport.get("brand") or "unknown")
    rows: list[dict[str, str]] = []
    for kind, values in (passport.get("entities") or {}).items():
        for value in values or []:
            rows.append({"Field": kind, "Detected value": value})
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.download_button(
        "Save Asset Passport",
        data=json.dumps(passport, ensure_ascii=False, indent=2),
        file_name=f"{name.rsplit('.', 1)[0]}_asset_passport.json",
        mime="application/json",
        use_container_width=True,
    )


def render_ocr_result(name: str, data: bytes, result: dict[str, Any]) -> None:
    confidence = float(result.get("confidence", 0.0))
    runtime = result.get("runtime") or (result.get("asset_passport") or {}).get("runtime", {})
    st.markdown(
        f'<div class="result-head"><strong>Challenge OCR complete</strong><br/><span>{safe(name)} · Qwen2.5-VL · AMD local inference</span></div>',
        unsafe_allow_html=True,
    )
    left, right = st.columns([1.12, 1], gap="large")
    with left:
        render_scan_image(data, name)
    with right:
        a, b = st.columns(2)
        a.metric("OCR confidence", f"{confidence * 100:.1f}%")
        b.metric("Processing", "AMD local")
        st.markdown("#### Recognized text")
        st.code(result.get("text", "") or "(empty)", language=None)
        render_passport(result.get("asset_passport") or {}, name)
        with st.expander("Runtime evidence"):
            st.json({"runtime": runtime, "info": result.get("info", {})})
    render_stack(runtime)


def render_analysis_result(name: str, data: bytes, result: dict[str, Any]) -> None:
    analysis = result.get("analysis") or {}
    passport = result.get("asset_passport") or {}
    runtime = result.get("runtime") or passport.get("runtime") or {}
    confidence = float(analysis.get("confidence", 0.0))

    st.markdown(
        f'<div class="result-head"><strong>Visual analysis complete</strong><br/><span>{safe(name)} · {safe(analysis.get("task", "general"))} · evidence-first AMD vision</span></div>',
        unsafe_allow_html=True,
    )
    left, right = st.columns([1.12, 1], gap="large")
    with left:
        render_scan_image(data, name)
    with right:
        a, b = st.columns(2)
        a.metric("Model confidence", f"{confidence * 100:.1f}%")
        b.metric("Object", analysis.get("object_type") or "unknown")
        if analysis.get("summary"):
            st.markdown("#### What InfraLens sees")
            st.write(analysis["summary"])

        if analysis.get("brand") or analysis.get("model"):
            brand, model = st.columns(2)
            brand.metric("Brand", analysis.get("brand") or "unknown")
            model.metric("Model", analysis.get("model") or "unknown")

        visible = analysis.get("visible_text") or []
        if visible:
            st.markdown("#### Visible text")
            st.code("\n".join(visible), language=None)

        identifiers = analysis.get("identifiers") or []
        if identifiers:
            st.markdown("#### Identifiers")
            st.dataframe(pd.DataFrame(identifiers), use_container_width=True, hide_index=True)

        observations = analysis.get("observations") or []
        if observations:
            st.markdown("#### Observations")
            for item in observations:
                st.markdown(f'<div class="observation">{safe(item)}</div>', unsafe_allow_html=True)

        warnings = analysis.get("warnings") or []
        if warnings:
            st.markdown("#### Review items")
            for item in warnings:
                st.markdown(f'<div class="observation warning">{safe(item)}</div>', unsafe_allow_html=True)

        render_passport(passport, name)
        with st.expander("Runtime evidence"):
            st.json({"runtime": runtime, "info": result.get("info", {}), "analysis_task": analysis.get("task")})

    render_stack(runtime)


render_top()

st.markdown('<div class="section-title">1. How do you want to capture?</div>', unsafe_allow_html=True)
st.markdown('<div class="section-copy">The camera belongs to the user device. The analysis happens on our AMD infrastructure.</div>', unsafe_allow_html=True)

source = st.radio(
    "Capture source",
    ["Use camera", "Upload photo", "Batch upload"],
    horizontal=True,
    label_visibility="collapsed",
)

st.markdown('<div class="section-title">2. What should InfraLens analyze?</div>', unsafe_allow_html=True)
analysis_mode = st.radio(
    "Analysis mode",
    list(ANALYSIS_MODES.keys()),
    horizontal=True,
    label_visibility="collapsed",
)
st.caption(ANALYSIS_MODES[analysis_mode]["copy"])

uploads: list[Any] = []
if source == "Use camera":
    captured = st.camera_input("Capture from this device")
    st.caption("Uses the camera exposed by the browser. On desktop this can be the built-in webcam or a connected USB camera selected by the browser/OS.")
    if captured:
        uploads = [captured]
elif source == "Upload photo":
    upload = st.file_uploader(
        "Upload one field image",
        type=["png", "jpg", "jpeg", "webp", "tif", "tiff"],
        accept_multiple_files=False,
    )
    if upload:
        uploads = [upload]
else:
    batch = st.file_uploader(
        "Upload several field images",
        type=["png", "jpg", "jpeg", "webp", "tif", "tiff"],
        accept_multiple_files=True,
    )
    uploads = list(batch or [])

st.markdown(
    """
    <div class="privacy">
      <span class="privacy-dot"></span>
      <div><strong>Transparent pipeline.</strong> Images are sent from this browser to our AMD 1.5 host and processed by Qwen2.5-VL on the Radeon AI PRO R9700. No third-party vision API receives the image.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if uploads:
    results: list[tuple[str, bytes, dict[str, Any], str]] = []
    task = ANALYSIS_MODES[analysis_mode]["task"]

    with st.status("Scanning on AMD…", expanded=False) as status:
        for index, upload in enumerate(uploads, start=1):
            data = upload.getvalue()
            name = getattr(upload, "name", None) or f"camera_capture_{index}.jpg"
            try:
                if task == "ocr" or source == "Batch upload":
                    result = call_ocr(data)
                    kind = "ocr"
                else:
                    result = call_analysis(data, task)
                    kind = "analysis"
                results.append((name, data, result, kind))
            except Exception as exc:
                st.error(f"{name}: {type(exc).__name__}: {exc}")
        if results:
            status.update(label=f"{len(results)} scan(s) completed on AMD", state="complete")
        else:
            status.update(label="No scan completed", state="error")

    if source == "Batch upload" and results:
        st.markdown('<div class="section-title">Batch inventory preview</div>', unsafe_allow_html=True)
        summary: list[dict[str, Any]] = []
        for name, _data, result, _kind in results:
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

    for name, data, result, kind in results:
        st.divider()
        if kind == "ocr":
            render_ocr_result(name, data, result)
        else:
            render_analysis_result(name, data, result)
else:
    render_stack()
    st.markdown(
        """
        <div class="section-title">Try something real</div>
        <div class="section-copy">
          Use a road sign for the official OCR challenge, an NVR or switch label for Asset Passport,
          or point the camera at any ordinary object for a general evidence-first visual analysis.
        </div>
        """,
        unsafe_allow_html=True,
    )
