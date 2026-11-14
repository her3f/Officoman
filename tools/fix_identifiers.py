#!/usr/bin/env python3
"""Repair identifiers that the bulk rename glued together.

The brand rename turns `ArtCraft` into `White Office`. Inside a code identifier
(`ArtCraftApi`, `ArtCraftLauncherData`) that leaves a space, which neither Rust nor
WiX nor TOML accepts. Display strings keep the space; identifiers lose it.

Run after tools/rebrand.py, tools/scrub_vendor.py, tools/rebrand_launcher.py and
tools/patch_launcher.py.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXTENSIONS = {".rs", ".toml", ".json", ".ps1", ".wxs", ".wxi", ".yml", ".yaml", ".wxl"}


def main() -> int:
    fixed = 0
    for p in (ROOT / "apps").rglob("*"):
        if not p.is_file() or p.suffix.lower() not in EXTENSIONS:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        # "White Office" glued to a following identifier char is a broken identifier.
        out = re.sub(r"White Office(?=[A-Za-z0-9_.])", "WhiteOffice", text)
        out = re.sub(r"(?<=[A-Za-z0-9_])White Office\b", "WhiteOffice", out)
        if out != text:
            p.write_text(out, encoding="utf-8")
            fixed += 1
    print(f"identifier repair: {fixed} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
