#!/usr/bin/env python3
"""Point the White Office Launcher at our four apps.

The launcher (>= v0.19.2) compiles its app list from `crates/core/catalog.toml`
via a build script; older versions kept it as a `pub const SUITE` in the source.
This script writes the catalog and fixes the remaining source constants, so it
works for both.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAUNCHER = ROOT / "apps" / "whiteoffice-launcher"
CORE = LAUNCHER / "crates" / "core" / "src"

CATALOG_TOML = '''# White Office Launcher catalog — the four apps, our own data.
# Read by crates/core/build.rs and compiled into the binary.

[[apps]]
id = "nib"
name = "Nib"
tagline = "Documents"
color = [51, 67, 155]
ink_light = [36, 47, 112]
ink_dark = [124, 140, 222]
repo = "her3f/officoman"
former_ids = []
former_names = []
kind = "official"
publisher = "White Office"
msi_publisher = "White Office"
former_bundles = []
site = "https://officoman.whitebearom.com/apps/nib.html"

[[apps]]
id = "tally"
name = "Tally"
tagline = "Spreadsheets"
color = [31, 122, 107]
ink_light = [21, 87, 76]
ink_dark = [104, 182, 166]
repo = "her3f/officoman"
former_ids = []
former_names = []
kind = "official"
publisher = "White Office"
msi_publisher = "White Office"
former_bundles = []
site = "https://officoman.whitebearom.com/apps/tally.html"

[[apps]]
id = "podium"
name = "Podium"
tagline = "Presentations"
color = [180, 80, 46]
ink_light = [130, 55, 30]
ink_dark = [233, 140, 105]
repo = "her3f/officoman"
former_ids = []
former_names = []
kind = "official"
publisher = "White Office"
msi_publisher = "White Office"
former_bundles = []
site = "https://officoman.whitebearom.com/apps/podium.html"

[[apps]]
id = "sheaf"
name = "Sheaf"
tagline = "PDF"
color = [107, 78, 158]
ink_light = [76, 54, 115]
ink_dark = [168, 140, 215]
repo = "her3f/officoman"
former_ids = []
former_names = []
kind = "official"
publisher = "White Office"
msi_publisher = "White Office"
former_bundles = []
site = "https://officoman.whitebearom.com/apps/sheaf.html"
'''

ICONS_BLOCK = '''pub fn app_icon_png(id: &str) -> Option<&'static [u8]> {
    Some(match id {
        "nib" => include_bytes!("../../../assets/app-icons/nib.png"),
        "tally" => include_bytes!("../../../assets/app-icons/tally.png"),
        "podium" => include_bytes!("../../../assets/app-icons/podium.png"),
        "sheaf" => include_bytes!("../../../assets/app-icons/sheaf.png"),
        _ => return None,
    })
}'''


def patch_file(path: Path, pairs: list[tuple[str, str]]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    done = []
    for old, new in pairs:
        if old in text:
            text = text.replace(old, new)
            done.append(old[:40])
    if done:
        path.write_text(text, encoding="utf-8")
    return done


def patch_mirror() -> None:
    """Bake the project's own server in as the release source.

    The upstream launcher only ever asks GitHub, and its loopback mirror is feature-gated.
    Without this, the launcher queries `her3f/officoman/releases`, finds the `ci-*` tags
    (which are not versions) and reports every app as "not found". This step must run
    after tools/rebrand_launcher.py, which copies the pristine file in.
    """
    backend = LAUNCHER / "crates" / "native" / "src" / "backend.rs"
    text = backend.read_text(encoding="utf-8")
    old = """fn local_mirror() -> Option<String> {
    if !cfg!(feature = "local-mirror") {
        return None;
    }"""
    new = """/// Where this project publishes its release feed and builds. Baked in at build time with
/// `WHITEOFFICE_LAUNCHER_MIRROR`, so the launcher asks this server and never GitHub.
const BUILT_IN_MIRROR: Option<&str> = option_env!("WHITEOFFICE_LAUNCHER_MIRROR");

fn local_mirror() -> Option<String> {
    if let Some(base) = BUILT_IN_MIRROR {
        let base = base.trim();
        if base.starts_with("https://") && !base.contains(['?', '#', '\\\\']) {
            return Some(if base.ends_with('/') { base.to_string() } else { format!("{base}/") });
        }
        log::warn!("ignoring the built-in mirror {base}: it must be an https:// base URL");
    }
    if !cfg!(feature = "local-mirror") {
        return None;
    }"""
    if old in text:
        backend.write_text(text.replace(old, new, 1), encoding="utf-8")
        print("  ok    mirror support (backend.rs)")
    else:
        print("  skip  mirror support (already present or signature changed)")


def main() -> int:
    if not LAUNCHER.is_dir():
        print(f"missing {LAUNCHER}", file=sys.stderr)
        return 1

    (LAUNCHER / "crates" / "core" / "catalog.toml").write_text(CATALOG_TOML, encoding="utf-8")
    print("  ok    catalog.toml (4 apps)")

    patch_mirror()

    cat = CORE / "catalog.rs"
    text = cat.read_text(encoding="utf-8")

    # legacy SUITE const (pre-v0.19.2) — remove it if the regex still finds it
    text, n = re.subn(r"pub const SUITE: \[CraftApp; \d+\] = \[.*?\n\];",
                      "pub const SUITE: [CraftApp; 4] = [];", text, count=1, flags=re.S)
    if n:
        cat.write_text(text, encoding="utf-8")
        print("  ok    legacy SUITE const cleared")

    pairs = [
        ('publisher: "White Office",\n        msi_publisher: None,',
         'publisher: "White Office",\n        msi_publisher: Some("White Office"),'),
        ("mac_team: Some(WHITEOFFICE_TEAM_ID),",
         "mac_team: None, // builds are unsigned"),
        ('pub const GITHUB_URL: &str = "https://github.com/her3f";',
         'pub const GITHUB_URL: &str = "https://github.com/her3f/officoman";'),
        ('pub const GITHUB_URL: &str = "https://github.com/storytold";',
         'pub const GITHUB_URL: &str = "https://github.com/her3f/officoman";'),
    ]
    done = patch_file(cat, pairs)

    # app_icon_png arms
    text = cat.read_text(encoding="utf-8")
    text, n2 = re.subn(r"pub fn app_icon_png\(id: &str\) -> Option<&'static \[u8\]> \{.*?\n\}",
                       ICONS_BLOCK, text, count=1, flags=re.S)
    if n2:
        cat.write_text(text, encoding="utf-8")
        done.append("app_icon_png")

    # SOCIAL links -> none
    text = cat.read_text(encoding="utf-8")
    text, n3 = re.subn(r"pub const SOCIAL: \[\(&str, &str\); \d+\] = \[.*?\n\];",
                       "pub const SOCIAL: [(&str, &str); 0] = [];", text, count=1, flags=re.S)
    if n3:
        cat.write_text(text, encoding="utf-8")
        done.append("SOCIAL")

    for d in done:
        print(f"  ok    {d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
