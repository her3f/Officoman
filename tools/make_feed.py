#!/usr/bin/env python3
"""Build `release_info.json` — the feed the launcher reads.

The launcher asks for `<mirror>release_info.json` and expects GitHub's release shape.
Everything it lists is served from the same mirror, so the download URLs point at our
own domain rather than GitHub.

    python tools/make_feed.py                 # writes dist/release_info.json
    python tools/make_feed.py --base https://whiteoffice.whitebearom.com/dl/
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from release_assets import latest_assets

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

# slug -> (display name, version)
APPS = {
    "nib": ("Nib", None),
    "tally": ("Tally", None),
    "podium": ("Podium", None),
    "sheaf": ("Sheaf", None),
}
REPO = "her3f/officoman"


def version_of(slug: str) -> str | None:
    version, _ = latest_assets(DIST, slug)
    return version or None


def assets_for(slug: str, base: str) -> list[dict]:
    out = []
    _, assets = latest_assets(DIST, slug)
    for p in sorted(assets.values()):
        out.append({
            "name": p.name,
            "size_bytes": p.stat().st_size,
            "download_url": f"{base}{p.name}",
            "sha256": sha256(p),
        })
    return out


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="https://whiteoffice.whitebearom.com/dl/")
    args = ap.parse_args()
    DIST.mkdir(parents=True, exist_ok=True)
    base = args.base if args.base.endswith("/") else args.base + "/"

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    apps: dict[str, dict] = {}
    for slug, (name, _) in APPS.items():
        ver = version_of(slug)
        assets = assets_for(slug, base)
        if not ver or not assets:
            print(f"  skip {slug} (no build)")
            continue
        apps[slug] = {
            "name": name,
            "repo": REPO,
            "latest_release": {
                "tag": f"v{ver}",
                "name": f"{name} {ver}",
                "published_at": now,
                "html_url": "",
                "prerelease": False,
                "notes_markdown": "",
                "assets": assets,
            },
            "app_last_fetched": now,
        }
        print(f"  {slug:7} v{ver}  {len(assets)} assets")

    feed = {
        "success": True,
        "release_info": {"apps": apps, "last_fetched": now},
        "app_renames": [],
        "repo_renames": [],
        "important_notices": {"announcements": [], "alerts": []},
    }
    out = DIST / "release_info.json"
    out.write_text(json.dumps(feed, indent=2), encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}  ({out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
