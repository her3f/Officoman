#!/usr/bin/env python3
"""Rebrand the four upstream Crafting Apps into the Officoman suite.

Reads  _vendor/<upstream>/   (fresh shallow clone)
Writes apps/<product>/       (rebranded copy)

One global rule set is applied to every repository, because the apps reference
each other by name. Rules run in this order, and the order matters:

  1. bundle identifiers          ai.storyteller.*      -> io.github.her3f.*
  2. links to the ArtCraft site  getartcraft.com/...   -> the Officoman site
  3. self references             storytold/<app>       -> her3f/officoman
  4. product names (4 apps)      DeckCraft / deckcraft / DECKCRAFT / Deckcraft
  5. parent brand                ArtCraft              -> Officoman

External dependencies that live under the storytold organisation
(craft-libs, egui, craft-fonts, craft-i18n) are deliberately left untouched:
they are third-party git dependencies of the build, not product branding, and
renaming them would break dependency resolution.
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENDOR = ROOT / "_vendor"
APPS = ROOT / "apps"
SITE = "https://her3f.github.io/officoman"
MONO = "https://github.com/her3f/officoman"

# upstream dir -> (slug, TitleCase)
REPOS = {
    "deckcraft": ("podium", "Podium"),
    "gridcraft": ("tally", "Tally"),
    "pdfcraft": ("sheaf", "Sheaf"),
    "wordcraft": ("nib", "Nib"),
}

# how each upstream product spells itself
OLD_TITLE = {
    "deckcraft": "DeckCraft",
    "gridcraft": "GridCraft",
    "pdfcraft": "PdfCraft",
    "wordcraft": "WordCraft",
}

SKIP_DIRS = {".git"}
SKIP_SUFFIX = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".icns", ".tiff", ".tif",
    ".webp", ".bmp", ".wasm", ".woff", ".woff2", ".ttf", ".otf", ".eot",
    ".pdf", ".zip", ".gz", ".bz2", ".xz", ".7z", ".mp4", ".mov", ".wav",
    ".mp3", ".sqlite", ".bin", ".pack", ".idx", ".DS_Store",
}


def case_forms(old: str, title: str) -> set[str]:
    """Every spelling of an app name that actually occurs in the tree."""
    forms = {
        old,                      # deckcraft
        old.capitalize(),         # Deckcraft   (WiX identifiers)
        old.upper(),              # DECKCRAFT
        title,                    # DeckCraft
        title.upper(),            # DECKCRAFT
        title.lower(),            # deckcraft
    }
    if old.startswith("pdf"):
        forms.add("PDFCraft")     # PDFCraft
    return forms


def build_rules() -> list[tuple[str, str]]:
    rules: list[tuple[str, str]] = []

    # 1. bundle identifiers
    rules += [
        ("ai.storyteller.", "io.github.her3f."),
        ("ai/storyteller/", "io/github/her3f/"),
        ("ai\\storyteller\\", "io\\github\\her3f\\"),
        # bare domain, e.g. <developer id="ai.storyteller"> in AppStream metainfo
        ("ai.storyteller", "io.github.her3f"),
    ]

    # 2. ArtCraft-owned destinations
    for old, (new, _title) in REPOS.items():
        rules.append((f"https://getartcraft.com/apps/{old}", f"{SITE}/apps/{new}.html"))
    rules += [
        ("https://getartcraft.com", SITE),
        ("getartcraft.com", "her3f.github.io/officoman"),
        ("discord.gg/artcraft", "github.com/her3f/officoman/discussions"),
        ("https://www.youtube.com/@OfficialArtCraftStudios", MONO),
        ("https://x.com/get_artcraft", MONO),
        ("https://www.linkedin.com/company/artcraft-ai", MONO),
    ]

    # 3. references to these repositories themselves (the scheme-carrying form first, or
    #    the bare replacement would double the scheme)
    for old in REPOS:
        rules += [
            (f"https://github.com/storytold/{old}", MONO),
            (f"github.com/storytold/{old}", MONO),
            (f"storytold/{old}", "her3f/officoman"),
            (f"storytold_{old}", "her3f_officoman"),
        ]

    # 4. product names, every casing that occurs
    for old, (new, _new_title) in REPOS.items():
        for form in sorted(case_forms(old, OLD_TITLE[old]), key=len, reverse=True):
            if form.isupper():
                rules.append((form, new.upper()))
            elif form.islower():
                rules.append((form, new))
            else:
                rules.append((form, new.capitalize()))

    # 5. parent brand
    rules += [
        ("ArtCraft", "Officoman"),
        ("artcraft", "officoman"),
        ("ARTCRAFT", "OFFICOMAN"),
        ("ArCraft", "Officoman"),
    ]

    # de-duplicate, first wins
    seen: dict[str, str] = {}
    for old, new in rules:
        if old not in seen:
            seen[old] = new
    return list(seen.items())


RULES = build_rules()


def is_text_file(path: Path) -> bool:
    if path.suffix.lower() in SKIP_SUFFIX:
        return False
    if path.name in {"DS_Store", ".DS_Store"}:
        return False
    try:
        with path.open("rb") as fh:
            chunk = fh.read(8192)
        return b"\x00" not in chunk
    except OSError:
        return False


def transform(text: str) -> str:
    for old, new in RULES:
        if old in text:
            text = text.replace(old, new)
    return text


def copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".git"),
                    copy_function=shutil.copy2)


def rebrand_contents(root: Path) -> tuple[int, int]:
    changed = scanned = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            path = Path(dirpath) / name
            if not is_text_file(path):
                continue
            scanned += 1
            try:
                text = path.read_bytes().decode("utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            out = transform(text)
            if out != text:
                path.write_bytes(out.encode("utf-8"))
                changed += 1
    return scanned, changed


def rename_paths(root: Path) -> int:
    renamed = 0
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        for name in filenames + dirnames:
            new_name = transform(name)
            if new_name != name:
                src = Path(dirpath) / name
                dst = Path(dirpath) / new_name
                if dst.exists() and dst != src:
                    print(f"  ! collision, keeping {src.name}", file=sys.stderr)
                    continue
                src.rename(dst)
                renamed += 1
    return renamed


def main() -> int:
    APPS.mkdir(exist_ok=True)
    total = 0
    for old, (new, _title) in REPOS.items():
        src = VENDOR / old
        if not src.is_dir():
            print(f"missing vendor dir: {src}", file=sys.stderr)
            return 1
        dst = APPS / new
        print(f"== {old} -> apps/{new}")
        copy_tree(src, dst)

        brand = dst / "docs" / "brand"
        if brand.is_dir():
            shutil.rmtree(brand)
            print("   removed docs/brand/")

        for stale in dst.glob("assets/app-icon/icon-source.*"):
            stale.unlink()
            print(f"   removed {stale.relative_to(ROOT)}")

        scanned, changed = rebrand_contents(dst)
        renamed = rename_paths(dst)
        print(f"   {scanned} text files scanned, {changed} rewritten, {renamed} paths renamed")
        total += changed
    print(f"\ndone: {total} files rewritten")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
