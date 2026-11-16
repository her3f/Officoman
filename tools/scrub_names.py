#!/usr/bin/env python3
"""Final white-label scrub: remove every trace of the previous project naming.

Replaces, in text files only:
  - the upstream brand (White Office -> White Office, case variants)
  - the upstream app names (Nib->Nib, Tally->Tally,
    Podium->Podium, Sheaf->Sheaf, and their lowercase forms)
  - upstream app repo references (storytold/<app> -> her3f/officoman)

Kept untouched:
  - Cargo.lock (dependency hashes + git sources must stay valid)
  - shared upstream infrastructure git deps (storytold/egui, storytold/craft-libs,
    storytold/craft-common-actions, storytold/craft-contrib, storytold/craft-fonts,
    storytold/craft-i18n, storytold/photocraft-corpus) — these are dependencies and
    shared tooling, not the previous project name
  - binary files (.DS_Store, images) — handled separately
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Keep these dependency/reference hosts; they are shared infrastructure, not branding.
KEEP_HOSTS = (
    "storytold/egui",
    "storytold/craft-libs",
    "storytold/craft-common-actions",
    "storytold/craft-contrib",
    "storytold/craft-fonts",
    "storytold/craft-i18n",
    "storytold/photocraft-corpus",
)

# Ordered: the most specific replacement first, so `White Office Launcher` becomes
# `White Office Launcher` before `White Office` becomes `White Office`.
RULES = [
    # upstream app repositories -> our monorepo
    ("her3f/officoman", "her3f/officoman"),
    ("her3f/officoman", "her3f/officoman"),
    ("her3f/officoman", "her3f/officoman"),
    ("her3f/officoman", "her3f/officoman"),
    ("her3f/officoman", "her3f/officoman"),
    # the brand, most specific first
    ("White Office Launcher", "White Office Launcher"),
    ("White Office", "White Office"),
    ("whiteoffice", "whiteoffice"),
    ("WHITEOFFICE", "WHITEOFFICE"),
    # old app names
    ("Nib", "Nib"),
    ("Tally", "Tally"),
    ("Podium", "Podium"),
    ("Sheaf", "Sheaf"),
    ("nib", "nib"),
    ("tally", "tally"),
    ("podium", "podium"),
    ("sheaf", "sheaf"),
]

SKIP_DIRS = {".git", "_vendor", "target", "dist", "node_modules", "__pycache__", ".dsh"}
SKIP_SUFFIXES = {".lock", ".DS_Store", ".png", ".ico", ".icns", ".jpg", ".jpeg",
                 ".gif", ".webp", ".exe", ".msi", ".zip", ".tar.gz", ".gz", ".wasm"}

TEXT_SUFFIXES = {".rs", ".md", ".toml", ".py", ".ps1", ".wxs", ".wxi", ".wxl", ".xml",
                 ".html", ".json", ".tsv", ".yml", ".yaml", ".js", ".cjs", ".txt", ".in",
                 ".sh", ".css", ".svg", ".rtf", ".metainfo"}


def protect_hosts(text: str) -> str:
    """Temporarily mask shared-infra hosts so the rules never touch them."""
    masks: list[str] = []
    def sub(m: re.Match) -> str:
        masks.append(m.group(0))
        return f"\x00{len(masks) - 1}\x00"
    for host in KEEP_HOSTS:
        text = re.sub(re.escape(host), sub, text)
    return text, masks


def restore_hosts(text: str, masks: list[str]) -> str:
    for i, host in enumerate(masks):
        text = text.replace(f"\x00{i}\x00", host)
    return text


def main() -> int:
    changed = 0
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.relative_to(ROOT).parts):
            continue
        if p.suffix.lower() in SKIP_SUFFIXES:
            continue
        if p.name == "Cargo.lock" or p.name.endswith(".lock"):
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        orig = text
        text, masks = protect_hosts(text)
        for old, new in RULES:
            text = text.replace(old, new)
        text = restore_hosts(text, masks)
        if text != orig:
            p.write_text(text, encoding="utf-8")
            changed += 1
    print(f"scrubbed {changed} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
