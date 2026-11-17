#!/usr/bin/env python3
"""Rebrand the upstream MailCraft repository into White Office's Courier.

Reads  _vendor/mailcraft/   (fresh shallow clone)
Writes apps/courier/        (rebranded copy)

Rules are applied as literal replacements, most specific first:

  1. bundle identifier     io.github.billsecond.mailcraft -> io.github.her3f.courier
  2. upstream repo/org     UCS-Care-Group/mailcraft       -> her3f/officoman
  3. app website           mailcraft.work                 -> whiteoffice.whitebearom.com
  4. publisher             UCS Care Group                -> White Office Team
  5. author handle         billsecond                    -> her3f
  6. product name          MailCraft / mailcraft / MAILCRAFT -> Courier / courier / COURIER
  7. parent brand          ArtCraft / artcraft            -> White Office / whiteoffice

File and directory names that contain `mailcraft` are renamed to `courier` as
well (crates and apps are named after the product).
"""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_vendor" / "mailcraft"
DST = ROOT / "apps" / "courier"
SITE = "https://whiteoffice.whitebearom.com"
MONO = "https://github.com/her3f/officoman"

SKIP_DIRS = {".git", "target", "node_modules", "__pycache__"}
SKIP_SUFFIX = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".icns", ".tiff", ".tif",
    ".webp", ".bmp", ".wasm", ".woff", ".woff2", ".ttf", ".otf", ".eot",
    ".pdf", ".zip", ".gz", ".bz2", ".xz", ".7z", ".mp4", ".mov", ".wav",
    ".mp3", ".sqlite", ".bin", ".pack", ".idx", ".DS_Store", ".lock",
}

# Most specific first: a longer string must win over its own substrings.
RULES: list[tuple[str, str]] = [
    # 1. bundle identifiers
    ("io.github.billsecond.mailcraft", "io.github.her3f.courier"),
    ("io.github.billsecond", "io.github.her3f"),
    ("io/github/billsecond", "io/github/her3f"),
    # 2. upstream repository / organisation
    ("UCS-Care-Group/mailcraft", "her3f/officoman"),
    ("UCS-Care-Group", "her3f/officoman"),
    ("UCS Care Group", "White Office Team"),
    ("UCS Care", "White Office"),
    ("UCS-Care", "White Office"),
    # 3. website
    ("https://mailcraft.work", SITE),
    ("http://mailcraft.work", SITE),
    ("mailcraft.work", "whiteoffice.whitebearom.com"),
    # 5. author handle
    ("billsecond", "her3f"),
    # 6. product name
    ("MAILCRAFT", "COURIER"),
    ("MailCraft", "Courier"),
    ("Mailcraft", "Courier"),
    ("mailcraft", "courier"),
    # 7. parent brand
    ("ArtCraft", "White Office"),
    ("artcraft", "whiteoffice"),
    ("ARTCRAFT", "WHITEOFFICE"),
]


def renamed(name: str) -> str:
    return name.replace("mailcraft", "courier").replace("MailCraft", "Courier")


def main() -> int:
    if not SRC.is_dir():
        raise SystemExit(f"missing {SRC} (clone UCS-Care-Group/mailcraft there first)")
    if DST.exists():
        shutil.rmtree(DST)
    shutil.copytree(SRC, DST, ignore=shutil.ignore_patterns(*SKIP_DIRS))

    # Rename directories and files whose names carry the product name (deepest first).
    for p in sorted(DST.rglob("*"), key=lambda q: len(q.parts), reverse=True):
        new_name = renamed(p.name)
        if new_name != p.name:
            p.rename(p.with_name(new_name))

    changed = 0
    for p in DST.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.relative_to(DST).parts):
            continue
        if p.suffix.lower() in SKIP_SUFFIX:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        original = text
        for old, new in RULES:
            text = text.replace(old, new)
        if text != original:
            p.write_text(text, encoding="utf-8")
            changed += 1

    print(f"rebranded {changed} files into {DST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
