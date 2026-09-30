#!/usr/bin/env python3
"""Safely add InfraLens Track 2 to the canonical cloudflared ingress config.

Default mode is dry-run. Use --apply to write, validate, and restart the matching
user cloudflared service when it can be identified unambiguously.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import pathlib
import shutil
import subprocess

HOSTNAME = "infralens.creatorcore.ai"
SERVICE = "http://192.168.1.5:18501"
DEFAULT_CONFIG = pathlib.Path.home() / ".cloudflared" / "opportunityops.yml"


def run(*argv: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def patch_config(text: str) -> str:
    if f"hostname: {HOSTNAME}" in text:
        return text
    marker = "  - service: http_status:404"
    if marker not in text:
        raise RuntimeError("catch-all ingress marker not found; refusing to guess insertion point")
    stanza = f"  - hostname: {HOSTNAME}\n    service: {SERVICE}\n"
    return text.replace(marker, stanza + marker, 1)


def validate(config: pathlib.Path) -> None:
    p = run("cloudflared", "tunnel", "--config", str(config), "ingress", "validate")
    if p.returncode != 0:
        raise RuntimeError(f"cloudflared ingress validation failed: {p.stderr.strip() or p.stdout.strip()}")


def discover_user_unit(config: pathlib.Path) -> str | None:
    p = run("systemctl", "--user", "list-units", "--type=service", "--all", "--no-legend", "--plain")
    if p.returncode != 0:
        return None
    candidates = []
    for line in p.stdout.splitlines():
        unit = line.split(None, 1)[0] if line.split() else ""
        if "cloudflared" not in unit.lower():
            continue
        show = run("systemctl", "--user", "show", unit, "-p", "ExecStart", "--value")
        if show.returncode == 0 and str(config) in show.stdout:
            candidates.append(unit)
    if len(candidates) == 1:
        return candidates[0]
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=pathlib.Path, default=DEFAULT_CONFIG)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    config = args.config.expanduser().resolve()
    if not config.is_file():
        raise SystemExit(f"config not found: {config}")

    original = config.read_text(encoding="utf-8")
    updated = patch_config(original)
    if updated == original:
        print(f"already configured: {HOSTNAME} -> {SERVICE}")
        return 0

    print(f"would add: {HOSTNAME} -> {SERVICE}")
    print(f"config: {config}")
    if not args.apply:
        print("dry-run only; rerun with --apply")
        return 0

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = config.with_name(config.name + f".before-infralens-{stamp}")
    shutil.copy2(config, backup)
    tmp = config.with_name(config.name + ".tmp-infralens")
    tmp.write_text(updated, encoding="utf-8")
    try:
        validate(tmp)
        os.replace(tmp, config)
        validate(config)
        unit = discover_user_unit(config)
        if unit:
            p = run("systemctl", "--user", "restart", unit)
            if p.returncode != 0:
                raise RuntimeError(f"failed restarting {unit}: {p.stderr.strip()}")
            print(f"restarted: {unit}")
        else:
            print("config updated and validated; matching user service not uniquely identifiable")
        print(f"backup: {backup}")
        print(f"configured: {HOSTNAME} -> {SERVICE}")
        return 0
    except Exception:
        if tmp.exists():
            tmp.unlink()
        shutil.copy2(backup, config)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
