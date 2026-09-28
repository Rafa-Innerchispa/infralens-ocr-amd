#!/usr/bin/env python3
"""Fail-closed physical acceptance harness for the AMD Academy MC2 image."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import time

REQUIRED_BASE = "rocm/pytorch:rocm10.0_ubuntu26.04_py3.14_pytorch_release_2.13.0"
IMAGE_LIMIT_GIB = 60.0
STARTUP_LIMIT_S = 600.0
PER_IMAGE_LIMIT_S = 30.0
VRAM_LIMIT_MIB = 48 * 1024

def run(args, *, timeout=None, env=None):
    return subprocess.run(args, text=True, capture_output=True, timeout=timeout, env=env)

def inspect(image):
    p=run(["docker","image","inspect",image])
    if p.returncode:
        raise RuntimeError(p.stderr.strip())
    return json.loads(p.stdout)[0]

def sample_vram(stop, samples):
    exe=shutil.which("rocm-smi")
    if not exe:
        return
    while not stop.is_set():
        p=run([exe,"--showmeminfo","vram","--json"])
        if p.returncode==0:
            try:
                payload=json.loads(p.stdout)
                for info in payload.values():
                    if not isinstance(info,dict):
                        continue
                    for key,value in info.items():
                        if "used" in key.lower() and "vram" in key.lower():
                            try:
                                n=int(str(value).split()[0])
                                if n>1024*1024:
                                    n//=1024*1024
                                samples.append(n)
                            except Exception:
                                pass
            except Exception:
                pass
        stop.wait(0.25)

def validate_output(path):
    data=json.loads(path.read_text(encoding="utf-8"))
    if set(data)!={"text","confidence"}:
        raise AssertionError(f"wrong JSON keys: {sorted(data)}")
    if not isinstance(data["text"],str):
        raise AssertionError("text must be string")
    if not isinstance(data["confidence"],(int,float)) or not 0<=float(data["confidence"])<=1:
        raise AssertionError("confidence out of range")
    return data

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--image",required=True)
    p.add_argument("--images",required=True)
    p.add_argument("--report",default="mc2_acceptance_report.json")
    p.add_argument("--expected-json",default="",help="optional filename -> exact normalized OCR text map")
    args=p.parse_args()

    expected={}
    if args.expected_json:
        expected=json.loads(Path(args.expected_json).read_text(encoding="utf-8"))

    fixtures_dir=Path(args.images).resolve()
    fixtures=sorted(x for x in fixtures_dir.iterdir() if x.suffix.lower() in {".png",".jpg",".jpeg",".tif",".tiff",".webp"})
    if not fixtures:
        raise SystemExit("no fixtures found")

    meta=inspect(args.image)
    report={
        "schema":"infralens.mc2_acceptance.v1",
        "image":args.image,
        "image_id":meta.get("Id"),
        "image_size_gib":round(meta.get("Size",0)/(1024**3),3),
        "limits":{"image_gib":IMAGE_LIMIT_GIB,"startup_s":STARTUP_LIMIT_S,"per_image_s":PER_IMAGE_LIMIT_S,"vram_mib":VRAM_LIMIT_MIB},
        "cases":[],
        "checks":{}
    }
    report["checks"]["image_size"]={"pass":report["image_size_gib"]<IMAGE_LIMIT_GIB}

    name=f"infralens-mc2-accept-{os.getpid()}"
    out=Path(tempfile.mkdtemp(prefix="infralens-mc2-out-"))
    stop=threading.Event()
    vram=[]
    thread=threading.Thread(target=sample_vram,args=(stop,vram),daemon=True)
    thread.start()

    start=time.perf_counter()
    proc=run([
        "docker","run","-d","--name",name,
        "--device=/dev/kfd","--device=/dev/dri","--group-add","video","--ipc=host",
        "-v",f"{fixtures_dir}:/app/input:ro","-v",f"{out}:/app/output",
        args.image
    ])
    if proc.returncode:
        report["checks"]["container_start"]={"pass":False,"stderr":proc.stderr[-4000:]}
        Path(args.report).write_text(json.dumps(report,indent=2)+"\n")
        return 2

    try:
        healthy=False
        deadline=time.monotonic()+STARTUP_LIMIT_S
        while time.monotonic()<deadline:
            h=run(["docker","exec",name,"python3","/app/healthcheck.py"])
            if h.returncode==0:
                healthy=True
                break
            state=run(["docker","inspect","-f","{{.State.Status}}",name])
            if state.returncode or state.stdout.strip() not in {"created","running"}:
                break
            time.sleep(2)
        startup=time.perf_counter()-start
        report["checks"]["startup"]={"pass":healthy and startup<STARTUP_LIMIT_S,"seconds":round(startup,3)}
        if not healthy:
            report["container_logs"]=run(["docker","logs",name]).stdout[-10000:]
        else:
            for src in fixtures:
                dest=out/f"{src.stem}_output.json"
                if dest.exists():
                    dest.unlink()
                started=time.perf_counter()
                try:
                    call=run([
                        "docker","exec",name,"python3","/app/app.py",
                        "--input-image",f"/app/input/{src.name}",
                        "--output-dir","/app/output"
                    ],timeout=PER_IMAGE_LIMIT_S+5)
                    elapsed=time.perf_counter()-started
                    case={"file":src.name,"seconds":round(elapsed,3),"returncode":call.returncode}
                    case["latency_pass"]=elapsed<PER_IMAGE_LIMIT_S
                    try:
                        payload=validate_output(dest)
                        case["json_pass"]=True
                        case["result"]=payload
                        wanted=expected.get(src.name)
                        if wanted is not None:
                            case["expected"]=wanted
                            case["exact_pass"]=payload["text"]==wanted
                        else:
                            case["exact_pass"]=True
                    except Exception as exc:
                        case["json_pass"]=False
                        case["json_error"]=f"{type(exc).__name__}: {exc}"
                    case["pass"]=call.returncode==0 and case["latency_pass"] and case["json_pass"] and case.get("exact_pass",False)
                except subprocess.TimeoutExpired:
                    case={"file":src.name,"seconds":PER_IMAGE_LIMIT_S+5,"returncode":None,"latency_pass":False,"json_pass":False,"pass":False,"error":"timeout"}
                report["cases"].append(case)

        peak=max(vram) if vram else None
        report["checks"]["peak_vram"]={"pass":peak is None or peak<=VRAM_LIMIT_MIB,"mib":peak,"samples":len(vram)}
        report["pass"]=all(x.get("pass",False) for x in report["checks"].values()) and bool(report["cases"]) and all(x["pass"] for x in report["cases"])
        Path(args.report).write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        print(json.dumps(report,indent=2,ensure_ascii=False))
        return 0 if report["pass"] else 4
    finally:
        stop.set()
        thread.join(timeout=2)
        run(["docker","rm","-f",name])
        shutil.rmtree(out,ignore_errors=True)

if __name__=="__main__":
    raise SystemExit(main())
