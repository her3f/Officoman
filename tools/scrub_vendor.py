#!/usr/bin/env python3
"""Second-pass cleanup that the plain text rebrand cannot do.

1. Replaces the upstream legal entity that appears in Windows/macOS binary metadata,
   AppStream and installer files. tools/rebrand.py swaps product names, but an LLC is
   not a product name, so it survived and would have shown up as the Publisher in
   Add/Remove Programs and in the .exe Properties dialog.

2. Drops the ATTRIBUTION entries for the brand assets that were deleted. Upstream's
   `cargo xtask assets` fails when a file is listed but missing, so leaving them would
   have broken the asset check.

Run after tools/rebrand.py, before tools/make_icons.py.
"""
from __future__ import annotations

import re
import sys

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    tomllib = None

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APPS = ROOT / "apps"

ENTITY = [
    ("Learning Machines LLC", "Officoman"),
    ("LearningMachinesInc", "Officoman"),
    ("learningmachines", "officoman"),
    ("LearningMachines", "Officoman"),
]

BRAND_DIR = "docs/brand/"
TEXT_EXT = {".md", ".toml", ".wxs", ".wxi", ".in", ".xml", ".json", ".ps1", ".rs", ".sh"}
SKIP = {".png", ".ico", ".icns", ".tiff", ".ttf", ".otf", ".wasm"}

# The apps describe themselves to the updater with a constant borrowed from the upstream
# `craft_update::suite` catalogue. Renaming that constant breaks the build, because the
# crate is an external dependency, and inheriting it would point this project's updates at
# the upstream repositories. Each app therefore spells its own entry out.
UPDATE_APP = {
    "nib": ("nib", "Nib", "Word processing and documents", "0x33, 0x43, 0x9b"),
    "tally": ("tally", "Tally", "Spreadsheets and data", "0x1f, 0x7a, 0x6b"),
    "podium": ("podium", "Podium", "Presentations and slide shows", "0xb4, 0x50, 0x2e"),
    "sheaf": ("sheaf", "Sheaf", "Reading, organizing and protecting PDFs", "0x6b, 0x4e, 0x9e"),
}

UPDATE_BLOCK = '''pub const UPDATE_APP: craft_update::app::App = craft_update::app::App {{
    icon_png: Some(include_bytes!("../../../assets/app-icon/hicolor/128x128/apps/io.github.her3f.{slug}.png")),
    accent: Some([{accent}]),
    developer: "Officoman",
    ..craft_update::app::App::new(
        "{slug}",
        "{name}",
        "{tagline}",
        "her3f/officoman",
    )
}};'''


def scrub_entity(path: Path) -> bool:
    if path.suffix.lower() in SKIP or not path.is_file():
        return False
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return False
    out = text
    for old, new in ENTITY:
        out = out.replace(old, new)
    if out != text:
        path.write_text(out, encoding="utf-8")
        return True
    return False


def drop_md_rows(path: Path) -> int:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    kept = [ln for ln in lines if BRAND_DIR not in ln]
    removed = len(lines) - len(kept)
    if removed:
        path.write_text("".join(kept), encoding="utf-8")
    return removed


def drop_toml_blocks(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    # split into blocks that start at a [[table]] header
    parts = re.split(r"(?m)^(?=\[\[)", text)
    kept, removed = [], 0
    for part in parts:
        if part.lstrip().startswith("[[") and BRAND_DIR in part:
            removed += 1
            continue
        kept.append(part)
    if removed:
        out = "".join(kept)
        path.write_text(out, encoding="utf-8")
        if tomllib is not None:
            try:
                tomllib.loads(out)
            except tomllib.TOMLDecodeError as exc:
                print(f"  ! {path.name} is not valid TOML after edit: {exc}", file=sys.stderr)
    return removed


def fix_update_app() -> int:
    """Replace the inherited craft_update::suite entry with an explicit one."""
    fixed = 0
    for slug, (ident, name, tagline, accent) in UPDATE_APP.items():
        path = APPS / slug / "crates" / "ui-egui" / "src" / "lib.rs"
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if "craft_update::suite::" not in text:
            continue
        new_block = UPDATE_BLOCK.format(slug=ident, name=name, tagline=tagline, accent=accent)
        new_text, n = re.subn(
            r"pub const UPDATE_APP: craft_update::app::App = craft_update::app::App \{.*?\n\};",
            new_block,
            text,
            count=1,
            flags=re.S,
        )
        if n:
            path.write_text(new_text, encoding="utf-8")
            fixed += 1
    return fixed


def main() -> int:
    if not APPS.is_dir():
        print("apps/ not found — run tools/rebrand.py first", file=sys.stderr)
        return 1

    entity_hits = 0
    md_rows = 0
    toml_blocks = 0

    for path in APPS.rglob("*"):
        if not path.is_file():
            continue
        if scrub_entity(path):
            entity_hits += 1
        if path.name.lower().startswith("attribution") or path.name.lower().startswith("licenses"):
            if path.suffix == ".md":
                md_rows += drop_md_rows(path)
            elif path.suffix == ".toml":
                toml_blocks += drop_toml_blocks(path)

    print(f"entity replaced in {entity_hits} files")
    print(f"removed {md_rows} attribution rows and {toml_blocks} TOML asset blocks")
    print(f"update entries rewritten in {fix_update_app()} apps")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
