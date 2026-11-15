#!/usr/bin/env python3
"""Rebrand the upstream Craft App Launcher into the White Office Launcher.

Reads  _vendor/craft-launcher/
Writes apps/whiteoffice-launcher/

Text substitution only. The catalog (which four apps the launcher knows about), the
per-app details data and the bundled icons are patched separately, because they are
structures rather than names.
"""
from __future__ import annotations

import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_vendor" / "craft-launcher"
DST = ROOT / "apps" / "whiteoffice-launcher"

SKIP_SUFFIX = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".icns", ".tiff", ".tif", ".webp",
    ".bmp", ".wasm", ".woff", ".woff2", ".ttf", ".otf", ".pdf", ".zip", ".gz",
}

# Longest / most specific first: the generic brand swap must not eat these.
RULES = [
    ("ai.storyteller.artcraft-launcher", "io.github.her3f.whiteoffice-launcher"),
    ("ai.storyteller.", "io.github.her3f."),
    ("ai/storyteller/", "io/github/her3f/"),
    ("ARTCRAFT_LAUNCHER_", "WHITEOFFICE_LAUNCHER_"),
    ("artcraft-launcher", "whiteoffice-launcher"),
    ("ArtCraft Launcher", "White Office Launcher"),
    ("ARTCRAFT TEAM", "WHITEOFFICE TEAM"),
    ("ARTCRAFT_TEAM_ID", "WHITEOFFICE_TEAM_ID"),
    ("ai.storyteller", "io.github.her3f"),
    ("Learning Machines LLC", "White Office"),
    # The launcher's own repository only. The upstream git dependencies (egui, craft-libs,
    # craft-fonts, craft-i18n) and the screenshot asset repo stay where they are: rewriting
    # them breaks dependency resolution.
    ("@SELF@", "her3f/officoman"),
    ("getartcraft.com", "officoman.whitebearom.com"),
    ("discord.gg/artcraft", "github.com/her3f/officoman/discussions"),
    ("ArtCraft", "White Office"),
    ("artcraft", "whiteoffice"),
    ("ARTCRAFT", "WHITEOFFICE"),
]


def is_text(path: Path) -> bool:
    if path.suffix.lower() in SKIP_SUFFIX:
        return False
    try:
        with path.open("rb") as fh:
            return b"\x00" not in fh.read(8192)
    except OSError:
        return False


def transform(text: str) -> str:
    # `storytold/craft-launcher` is this project's own repo; `storytold/craft-launcher-assets`
    # is a different, upstream repository, so the trailing lookahead keeps them apart.
    text = re.sub(r"storytold/craft-launcher(?!-)", "@SELF@", text)
    for old, new in RULES:
        if old in text:
            text = text.replace(old, new)
    return text


def main() -> int:
    if not SRC.is_dir():
        print(f"missing {SRC}", file=sys.stderr)
        return 1
    if DST.exists():
        shutil.rmtree(DST)
    shutil.copytree(SRC, DST, ignore=shutil.ignore_patterns(".git"),
                    copy_function=shutil.copy2)

    brand = DST / "docs" / "brand"
    if brand.is_dir():
        shutil.rmtree(brand)
        print("removed docs/brand/")

    changed = 0
    for dirpath, _dirnames, filenames in os.walk(DST):
        for name in filenames:
            path = Path(dirpath) / name
            if not is_text(path):
                continue
            try:
                text = path.read_bytes().decode("utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            out = transform(text)
            if out != text:
                path.write_bytes(out.encode("utf-8"))
                changed += 1

    renamed = 0
    for dirpath, dirnames, filenames in os.walk(DST, topdown=False):
        for name in filenames + dirnames:
            new_name = transform(name)
            if new_name != name:
                src = Path(dirpath) / name
                dst = Path(dirpath) / new_name
                if dst.exists():
                    print(f"  ! collision {name}", file=sys.stderr)
                    continue
                src.rename(dst)
                renamed += 1

    print(f"launcher: {changed} files rewritten, {renamed} paths renamed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

