"""Static website renderer. No network, packages, or application README writes."""
from __future__ import annotations

import argparse
import html
import json
import shutil
from pathlib import Path

from release_assets import latest_assets
from localize_site import build_locales
from site_design import home, app_page, apps_page, downloads

ROOT = Path(__file__).resolve().parent.parent
SITE_URL = "https://whiteoffice.whitebearom.com"
SOURCE = Path(__file__).resolve().parent / "site"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def page(title: str, body: str, path: str, description: str) -> str:
    root = "../" if path.startswith("apps/") else ""
    active = "apps" if path.startswith("apps/") else path.removesuffix(".html")
    current = ' aria-current="page"'
    nav = "".join(f'<a href="{root}{href}"'
                  f'{current if active == key else ""}>{label}</a>'
                  for key, href, label in (("apps", "apps/index.html", "The apps"),
                                          ("download", "download.html", "Download ↗")))
    return f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0b1422">
<title>{esc(title)}</title><meta name="description" content="{esc(description)}">
<link rel="canonical" href="{SITE_URL}/{path}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="website"><meta property="og:url" content="{SITE_URL}/{path}">
<link rel="icon" href="{root}assets/whiteoffice-mark.svg" type="image/svg+xml">
<link rel="stylesheet" href="{root}assets/style.css"><script src="{root}assets/site.js" defer></script>
</head><body>
<a class="skip" href="#main">Skip to content</a>
<header class="site"><div class="wrap header-inner">
<div class="brand-lockup"><a class="brand" href="{root}index.html"><img src="{root}assets/whiteoffice-mark.svg" width="34" height="34" alt="">White Office<span class="brand-dot" aria-hidden="true">.</span></a><a class="parent-brand" href="https://whitebearom.com/">A White Bear product</a></div>
<button class="menu-toggle" type="button" aria-expanded="false" aria-controls="navigation" hidden>Menu <span aria-hidden="true">☰</span></button>
<nav id="navigation" aria-label="Main navigation">{nav}</nav>
</div></header>
<main id="main">{body}</main>
<footer class="site"><div class="wrap footer-main"><div class="footer-identity"><a class="brand footer-brand" href="{root}index.html"><img src="{root}assets/whiteoffice-mark.svg" width="30" height="30" alt="">White Office</a><p>A little more room for your work.</p><a class="company-logo" href="https://whitebearom.com/"><img src="{root}assets/whitebear-logo.png" width="190" height="67" alt="White Bear Development"></a></div>
<div class="footer-links"><a href="{root}apps/index.html">Explore the apps</a><a href="https://whitebearom.com/">White Bear Development ↗</a></div></div>
<div class="wrap footer-bottom"><span>© 2026 White Office contributors</span><span>Built in Rust. Made for your desktop.</span></div></footer>
</body></html>'''


def release_catalog(dist: Path) -> dict:
    result = {}
    for slug in ("whiteoffice-launcher", "nib", "tally", "podium", "sheaf"):
        version, assets = latest_assets(dist, slug)
        if assets:
            result[slug] = {"version": version, "assets": {suffix: {"name": p.name, "size": p.stat().st_size} for suffix, p in assets.items()}}
    return result


def build(apps: list[dict], site: Path, catalog: dict) -> None:
    (site / "apps").mkdir(parents=True, exist_ok=True)
    (site / "assets" / "icons").mkdir(parents=True, exist_ok=True)
    for name in ("style.css", "site.js", "whitebear-logo.png"):
        shutil.copyfile(SOURCE / name, site / "assets" / name)
    shutil.copytree(SOURCE / 'fonts', site / 'assets' / 'fonts', dirs_exist_ok=True)
    for name in ("whiteoffice-mark.svg", "whiteoffice-wordmark.svg"):
        shutil.copyfile(ROOT / "brand" / name, site / "assets" / name)
    for a in apps:
        shutil.copyfile(ROOT / "apps" / a['slug'] / "assets" / "app-icon" / "hicolor" / "256x256" / "apps" / f"io.github.her3f.{a['slug']}.png", site / "assets" / "icons" / f"{a['slug']}.png")
    pages = [("index.html", "White Office — A little more room for your work", home(apps), "Four independent apps for documents, spreadsheets, presentations and PDF. Explore White Office and download builds for Windows, macOS and Linux."),
             ("apps/index.html", "The apps — White Office", apps_page(apps), "Meet Nib, Tally, Podium and Sheaf: the four independent White Office applications."),
             ("download.html", "Download — White Office", downloads(apps, catalog), "Choose White Office packages for Windows, macOS and Linux, with installers and portable downloads.")]
    pages += [(f'apps/{a["slug"]}.html', f'{a["name"]} — White Office', app_page(a, apps), a['tagline']) for a in apps]
    for path, title, body, description in pages:
        (site / path).write_text(page(title, body, path, description), encoding="utf-8")
    (site / ".nojekyll").write_text("", encoding="utf-8")
    (site / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{SITE_URL}/{p[0]}</loc></url>' for p in pages) + '</urlset>\n', encoding="utf-8")
    (site / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    build_locales(site)


def main(apps: list[dict]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "docs")
    parser.add_argument("--refresh-releases", action="store_true", help="Explicitly refresh the tracked download catalog from local dist artifacts")
    args = parser.parse_args()
    manifest = SOURCE / "releases.json"
    if args.refresh_releases:
        catalog = release_catalog(ROOT / "dist")
        if not catalog:
            parser.error("dist has no release artifacts; existing catalog was preserved")
        manifest.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    catalog = json.loads(manifest.read_text(encoding="utf-8")) if manifest.exists() else {}
    build(apps, args.output, catalog)
    print(f"Built English and Arabic pages in {args.output}; application READMEs unchanged.")
    return 0
