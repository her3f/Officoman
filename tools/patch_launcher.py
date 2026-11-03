#!/usr/bin/env python3
"""Point the Officoman Launcher at our four apps.

The rebrand (tools/rebrand_launcher.py) only changes names. This changes structure:
the catalog becomes four apps instead of seventeen, the suite list, the icons, the
per-app details data, and the publisher/signing assumptions.

Idempotent: each edit is keyed on a marker and reports whether it applied.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAUNCHER = ROOT / "apps" / "officoman-launcher"
CORE = LAUNCHER / "crates" / "core" / "src"

SUITE_BLOCK = '''pub const SUITE: [CraftApp; 4] = [
    app(
        "nib",
        "Nib",
        "Documents",
        [[0x33, 0x43, 0x9b], [0x24, 0x2f, 0x70], [0x6b, 0x7d, 0xd6]],
        "her3f/officoman",
    ),
    app(
        "tally",
        "Tally",
        "Spreadsheets",
        [[0x1f, 0x7a, 0x6b], [0x15, 0x57, 0x4c], [0x4f, 0xc2, 0xae]],
        "her3f/officoman",
    ),
    app(
        "podium",
        "Podium",
        "Presentations",
        [[0xb4, 0x50, 0x2e], [0x8a, 0x3a, 0x1f], [0xe8, 0x8a, 0x63]],
        "her3f/officoman",
    ),
    app(
        "sheaf",
        "Sheaf",
        "PDF",
        [[0x6b, 0x4e, 0x9e], [0x4d, 0x37, 0x76], [0xa5, 0x8a, 0xd6]],
        "her3f/officoman",
    ),
];'''

ICONS_BLOCK = '''pub fn app_icon_png(id: &str) -> Option<&'static [u8]> {
    Some(match id {
        "nib" => include_bytes!("../../../assets/app-icons/nib.png"),
        "tally" => include_bytes!("../../../assets/app-icons/tally.png"),
        "podium" => include_bytes!("../../../assets/app-icons/podium.png"),
        "sheaf" => include_bytes!("../../../assets/app-icons/sheaf.png"),
        _ => return None,
    })
}'''

DETAILS_BLOCK = '''pub const DETAILS: [AppDetails; 0] = [];'''


def replace_between(text: str, start: str, end: str, new: str) -> tuple[str, bool]:
    """Replace start..=end (end is the literal that closes the block)."""
    i = text.find(start)
    if i < 0:
        return text, False
    j = text.find(end, i)
    if j < 0:
        return text, False
    return text[:i] + new + text[j + len(end):], True


def replace_once(text: str, old: str, new: str) -> tuple[str, bool]:
    if old not in text:
        return text, False
    return text.replace(old, new, 1), True


def main() -> int:
    if not CORE.is_dir():
        print(f"missing {CORE}", file=sys.stderr)
        return 1

    cat = CORE / "catalog.rs"
    text = cat.read_text(encoding="utf-8")
    applied = []

    text, ok = replace_between(
        text, "pub const SUITE: [CraftApp; 17] = [", "\n];", SUITE_BLOCK
    )
    applied.append(("suite", ok))

    text, ok = replace_between(
        text, "pub fn app_icon_png(id: &str) -> Option<&'static [u8]> {", "\n}", ICONS_BLOCK
    )
    applied.append(("icons", ok))

    text, ok = replace_once(
        text,
        'publisher: "Officoman",\n        msi_publisher: None,',
        'publisher: "Officoman",\n        msi_publisher: Some("Officoman"),',
    )
    applied.append(("msi publisher", ok))

    text, ok = replace_once(
        text,
        "mac_team: Some(OFFICOMAN_TEAM_ID),",
        "// These builds are not code-signed, so macOS installs are not offered.\n        mac_team: None,",
    )
    applied.append(("mac team", ok))

    text, ok = replace_once(
        text, '"her3f/craft-launcher"', '"her3f/officoman"'
    )
    if ok:
        text = text.replace('"her3f/craft-launcher"', '"her3f/officoman"')
    applied.append(("launcher repo", ok))

    text, ok = replace_between(
        text, "pub const SOCIAL: [(&str, &str); 5] = [", "\n];",
        "pub const SOCIAL: [(&str, &str); 0] = [];",
    )
    applied.append(("social links", ok))

    text, ok = replace_once(
        text,
        'pub const GITHUB_URL: &str = "https://github.com/her3f";',
        'pub const GITHUB_URL: &str = "https://github.com/her3f/officoman";',
    )
    applied.append(("github url", ok))

    text, ok = replace_once(
        text, 'pub const GITHUB_OWNER: &str = "storytold";',
        'pub const GITHUB_OWNER: &str = "her3f";'
    )
    applied.append(("github owner", ok))

    text, ok = replace_once(
        text, 'pub const GITHUB_URL: &str = "https://github.com/storytold";',
        'pub const GITHUB_URL: &str = "https://github.com/her3f/officoman";'
    )
    applied.append(("github url (unreplaced)", ok))

    cat.write_text(text, encoding="utf-8")

    det = CORE / "details.rs"
    if det.is_file():
        text = det.read_text(encoding="utf-8")
        text, ok = replace_between(
            text, "pub const DETAILS: [AppDetails; 17] = [", "\n];", DETAILS_BLOCK
        )
        applied.append(("details data", ok))
        det.write_text(text, encoding="utf-8")

    for name, ok in applied:
        print(f"  {'ok  ' if ok else 'skip'}  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
