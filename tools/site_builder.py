"""Static website renderer. No network, packages, or application README writes."""
from __future__ import annotations

import argparse
import html
import json
import shutil
from pathlib import Path

from release_assets import latest_assets
from localize_site import build_locales

ROOT = Path(__file__).resolve().parent.parent
SITE_URL = "https://officoman.whitebearom.com"
REPO = "https://github.com/her3f/officoman"
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
<meta name="theme-color" content="#f7f8fc">
<title>{esc(title)}</title><meta name="description" content="{esc(description)}">
<link rel="canonical" href="{SITE_URL}/{path}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="website"><meta property="og:url" content="{SITE_URL}/{path}">
<link rel="icon" href="{root}assets/whiteoffice-mark.svg" type="image/svg+xml">
<link rel="stylesheet" href="{root}assets/style.css"><script src="{root}assets/site.js" defer></script>
</head><body>
<a class="skip" href="#main">Skip to content</a>
<header class="site"><div class="wrap header-inner">
<a class="brand" href="{root}index.html"><img src="{root}assets/whiteoffice-mark.svg" width="34" height="34" alt="">White Office<span class="brand-dot" aria-hidden="true">.</span></a>
<button class="menu-toggle" type="button" aria-expanded="false" aria-controls="navigation" hidden>Menu <span aria-hidden="true">☰</span></button>
<nav id="navigation" aria-label="Main navigation">{nav}</nav>
</div></header>
<main id="main">{body}</main>
<footer class="site"><div class="wrap footer-main"><div><a class="brand" href="{root}index.html"><img src="{root}assets/whiteoffice-mark.svg" width="28" height="28" alt="">White Office</a><p>A little more room for your work.</p></div>
<div class="footer-links"><a href="{root}apps/index.html">Explore the apps</a><a href="{REPO}">Source on GitHub ↗</a></div></div>
<div class="wrap footer-bottom"><span>© 2026 White Office contributors</span><span>Built in Rust. Made for your desktop.</span></div></footer>
</body></html>'''


def card(app: dict, root: str = "") -> str:
    return f'''<a class="app-card" style="--accent:{app['accent']}" href="{root}apps/{app['slug']}.html">
<div class="card-top"><img src="{root}assets/icons/{app['slug']}.png" width="58" height="58" alt=""><span aria-hidden="true">↗</span></div>
<p class="eyebrow">{app['role']}</p><h3>{app['name']}</h3><p>{esc(app['tagline'])}</p>
<span class="card-link">Meet {app['name']} <span aria-hidden="true">→</span></span></a>'''


def preview(slug: str) -> str:
    if slug == "nib":
        return '''<div class="document-preview"><span class="doc-label">FIELD NOTES / 001</span><h3>Space for<br>your next idea.</h3><p>Good work starts with a blank page.<br>Make this one yours.</p><div class="ink-lines"><i></i><i></i><i></i></div><blockquote>Less getting in the way.<br>More getting it down.</blockquote><span class="doc-page">WHITE OFFICE <span>01</span></span></div>'''
    if slug == "tally":
        return '''<div class="sheet-preview"><div class="formula">ƒx <span>=SUM(B2:B5)</span></div><table><caption>Project budget · example data</caption><thead><tr><th scope="col">Project</th><th scope="col">Budget</th><th scope="col">Status</th></tr></thead><tbody><tr><td>Research</td><td>1,200</td><td>Complete</td></tr><tr><td>Design</td><td>2,800</td><td>In progress</td></tr><tr><td>Development</td><td>4,000</td><td>In progress</td></tr><tr><td>Launch</td><td>2,000</td><td>Planned</td></tr><tr><th scope="row">Total</th><td class="selected-cell">10,000</td><td></td></tr></tbody></table><div class="mini-chart" aria-label="Illustrative budget chart"><i style="height:30%"></i><i style="height:70%"></i><i style="height:100%"></i><i style="height:50%"></i></div></div>'''
    if slug == "podium":
        return '''<div class="slide-preview"><span>THE NEXT CHAPTER</span><h3>Small ideas.<br>Big possibilities.</h3><div class="slide-circle" aria-hidden="true"></div><p>A new perspective starts here.</p><small>WHITE OFFICE <span>01 / 12</span></small></div>'''
    return '''<div class="pdf-preview"><div class="pdf-thumbs"><span>01</span><span>02</span><span>03</span></div><div class="pdf-page"><span class="doc-label">PROJECT BRIEF</span><h3>Every page.<br>In its place.</h3><div class="ink-lines"><i></i><i></i><i></i></div><div class="highlight">A clearer view of the details.</div><div class="ink-lines"><i></i><i></i><i></i></div><span class="doc-page">REVIEW COPY · 01</span></div></div>'''


def home(apps: list[dict]) -> str:
    tabs = ''.join(f'<button type="button" id="tab-{a["slug"]}" role="tab" aria-selected="{str(i == 0).lower()}" aria-controls="panel-{a["slug"]}" tabindex="{0 if i == 0 else -1}"><img src="assets/icons/{a["slug"]}.png" width="24" height="24" alt="">{a["name"]}</button>' for i, a in enumerate(apps))
    panels = ''.join(f'<div id="panel-{a["slug"]}" role="tabpanel" aria-labelledby="tab-{a["slug"]}" tabindex="0" {"hidden" if i else ""}><div class="preview-toolbar"><span>{a["role"]}</span><span>White Office / {a["name"]}</span></div>{preview(a["slug"])}</div>' for i, a in enumerate(apps))
    return f'''<div class="wrap hero home-hero"><div class="hero-copy"><p class="eyebrow"><span class="status-dot"></span> YOUR WORK. YOUR SPACE.</p>
<h1>Big ideas.<br>Less busywork.<br><em>One office.</em></h1>
<p class="lede">A thoughtful home for your documents, spreadsheets, presentations and PDFs. Four independent apps, built to work beautifully together.</p>
<div class="cta"><a class="btn" href="download.html">Get White Office <span aria-hidden="true">↗</span></a><a class="text-link" href="#apps">Explore the apps <span aria-hidden="true">↓</span></a></div>
<p class="hero-note">Windows, macOS &amp; Linux <span>·</span> No account needed</p></div>
<div class="workspace-preview"><div class="window-bar"><span class="window-dots" aria-hidden="true">● ● ●</span><span>Your next great idea</span><span aria-hidden="true">↗</span></div><div class="app-tabs" role="tablist" aria-label="Explore an illustrative app preview">{tabs}</div>{panels}<div class="preview-caption"><span class="status-dot"></span> A little preview of what you can make <span>Illustration</span></div></div></div>
<div class="trust-strip"><div class="wrap"><span>LOCAL FILES. REAL POSSIBILITIES.</span><b>Works offline</b><b>Familiar file formats</b><b>Open source</b><b>Native performance</b></div></div>
<section class="wrap section" id="apps"><div class="section-heading"><div><p class="eyebrow">MEET YOUR NEW DESK</p><h2>Four apps. A whole lot possible.</h2></div><p>Start with what you need.<br>There’s room for the rest.</p></div><div class="app-grid">{''.join(card(a) for a in apps)}</div></section>
<section class="wrap section philosophy"><div><p class="eyebrow">LESS FRICTION, MORE FOCUS</p><h2>Tools that fit<br>the way you work.</h2><p class="lede">Your files belong on your desk. Your attention belongs on your ideas.</p></div><div class="principles"><article><span>01</span><div><h3>At home on your computer</h3><p>Native Rust applications for everyday desktop work. Open an app and get straight to it.</p></div></article><article><span>02</span><div><h3>Your work stays with you</h3><p>Create and edit local files without an account. Keep working when the connection doesn’t.</p></div></article><article><span>03</span><div><h3>Files you already know</h3><p>Work with DOCX, XLSX, PPTX and PDF. Bring your existing files and export work you can share.</p></div></article></div></section>
<section class="wrap"><div class="download-banner"><div><p class="eyebrow">MAKE YOURSELF AT HOME</p><h2>Your next project starts here.</h2><p>Choose your apps. Find your flow.</p></div><a class="btn light" href="download.html">Find your download ↗</a></div></section>'''


def about(apps: list[dict]) -> str:
    rows = ''.join(f'<tr><th scope="row">{a["name"]}</th><td><a href="https://github.com/storytold/{a["upstream"].lower()}">{a["upstream"]} ↗</a></td><td>MIT OR Apache-2.0</td></tr>' for a in apps)
    return f'''<div class="wrap hero"><p class="eyebrow">OUR STORY</p><h1>A new desk.<br><em>Open foundations.</em></h1><p class="lede">White Office is an independent fork of four Crafting Apps. A new identity, familiar file formats, and source code you can explore.</p></div>
<section class="wrap section prose"><h2>Built on the work of others</h2><p>Nib, Tally, Podium and Sheaf are derived from the projects below, published by the White Office team and their contributors. The source is dual-licensed under MIT or Apache-2.0; third-party components keep their respective licences.</p><div class="table-scroll" role="region" aria-label="Upstream projects" tabindex="0"><table><thead><tr><th scope="col">White Office</th><th scope="col">Upstream project</th><th scope="col">Source licence</th></tr></thead><tbody>{rows}</tbody></table></div><p><a href="{REPO}/blob/main/NOTICE">Read the repository notices ↗</a> and each app’s attribution records for details.</p></section>
<section class="wrap section"><div class="section-heading"><h2>A distinct identity.</h2><p>Same foundations. A project of its own.</p></div><div class="feature-grid"><article><h3>New names &amp; artwork</h3><p>Four app names and a shared White Office visual identity, with original icons and wordmarks.</p></article><article><h3>Independent packaging</h3><p>Application identifiers, installers and project links point to White Office.</p></article><article><h3>Source you can inspect</h3><p>Each application has its own Rust workspace. Explore the code, build it, and follow its development.</p></article></div></section>
<section class="wrap section prose"><h2>Attribution, without affiliation.</h2><p>White Office is not affiliated with or endorsed by the upstream White Office team. Upstream names are mentioned to identify the original projects. Their trademarks and artwork are distinct from the White Office brand.</p><a class="btn ghost" href="{REPO}">Explore the repository ↗</a></section>'''


def app_page(app: dict, apps: list[dict]) -> str:
    features = ''.join(f'<article><h3>{esc(t)}</h3><p>{esc(d)}</p></article>' for t, d in app['features'])
    return f'''<div class="wrap hero app-hero" style="--accent:{app['accent']}"><a class="back-link" href="index.html">← All apps</a><div class="app-title"><img src="../assets/icons/{app['slug']}.png" width="88" height="88" alt=""><div><p class="eyebrow">{app['role']}</p><h1>{app['name']}</h1></div></div><h2>{esc(app['tagline'])}</h2><p class="lede">{esc(app['lede'])}</p><div class="cta"><a class="btn" href="../download.html#{app['slug']}">Get {app['name']} ↗</a><a class="text-link" href="{REPO}/tree/main/apps/{app['slug']}">View source →</a></div></div>
<section class="wrap section"><p class="eyebrow">FAMILIAR FILES</p><p class="formats">{esc(app['formats'])}</p></section><section class="wrap section"><div class="section-heading"><h2>Made for your everyday work.</h2></div><div class="feature-grid">{features}</div></section>
<section class="wrap section prose"><h2>A work in progress, ready to explore.</h2><p>{app['name']} is an independent fork of {app['upstream']}. Desktop packages are listed on the download page when available. Compatibility and features continue to evolve; keep a copy of important files when trying a new build.</p></section>
<section class="wrap section"><div class="section-heading"><h2>The rest of your desk.</h2></div><div class="app-grid three">{''.join(card(a, '../') for a in apps if a != app)}</div></section>'''


def release_catalog(dist: Path) -> dict:
    result = {}
    for slug in ("whiteoffice-launcher", "nib", "tally", "podium", "sheaf"):
        version, assets = latest_assets(dist, slug)
        if assets:
            result[slug] = {"version": version, "assets": {suffix: {"name": p.name, "size": p.stat().st_size} for suffix, p in assets.items()}}
    return result


def downloads(apps: list[dict], catalog: dict) -> str:
    rows = []
    for a in [{"slug": "whiteoffice-launcher", "name": "Launcher", "role": "Install & update the suite"}, *apps]:
        data = catalog.get(a['slug'], {})
        assets = data.get('assets', {})
        cells = []
        for os, formats in (("windows", (("windows-x64.msi", "Installer", False), ("windows-x64-portable.zip", "Portable ZIP", True))), ("macos", (("macos-universal.tar.gz", "Universal archive", False),)), ("linux", (("linux-x86_64.tar.gz", "Linux archive", False),))):
            links = []
            for suffix, label, ghost in formats:
                asset = assets.get(suffix)
                if asset:
                    links.append(f'<a class="download-link {"secondary" if ghost else ""}" href="{SITE_URL}/dl/{esc(asset["name"])}" aria-label="Download {a["name"]} {esc(data["version"])} {os} {label}">{label} <span>↓</span></a><span class="file-size">{asset["size"] / 1e6:.1f} MB</span>')
            cells.append(f'<td data-platform="{os}">{"".join(links) or "<span class=unavailable>Not available yet</span>"}</td>')
        icon = f'<img src="assets/icons/{a["slug"]}.png" width="34" height="34" alt="">' if a['slug'] != 'whiteoffice-launcher' else '<img src="assets/whiteoffice-mark.svg" width="34" height="34" alt="">'
        rows.append(f'<tr id="{a["slug"]}"><th scope="row"><div class="download-app">{icon}<div>{a["name"]}<span>{esc(a["role"])}</span><code>{esc(data.get("version", "Coming soon"))}</code></div></div></th>{"".join(cells)}</tr>')
    return f'''<div class="wrap hero"><p class="eyebrow">MAKE ROOM FOR GOOD WORK</p><h1>Your desk.<br><em>Your download.</em></h1><p class="lede">Get the launcher to install and update your apps, or choose an individual app. No account. Just your next project.</p><div class="platform-filter" role="group" aria-label="Filter downloads by operating system" hidden><button type="button" data-os="all" aria-pressed="true">All platforms</button><button type="button" data-os="windows" aria-pressed="false">Windows</button><button type="button" data-os="macos" aria-pressed="false">macOS</button><button type="button" data-os="linux" aria-pressed="false">Linux</button></div></div>
<section class="wrap download-section"><p class="eyebrow" id="download-status" aria-live="polite">BUILDS FOR EVERY DESK</p><div class="table-scroll" role="region" aria-label="Application downloads" tabindex="0"><table class="downloads"><caption class="sr-only">White Office packages by application and platform</caption><thead><tr><th scope="col">Application</th><th scope="col" data-platform="windows">Windows <span>x64</span></th><th scope="col" data-platform="macos">macOS <span>Apple silicon + Intel</span></th><th scope="col" data-platform="linux">Linux <span>x86_64</span></th></tr></thead><tbody>{''.join(rows)}</tbody></table></div><p class="download-note">Available packages are listed per release. A missing platform means a package for that version is not available yet.</p></section>
<section class="wrap section"><div class="section-heading"><h2>A few things before you start.</h2></div><div class="feature-grid"><article><span class="step-number">01</span><h3>Pick your package</h3><p>On Windows, use the MSI installer for shortcuts and file associations, or extract the portable ZIP. macOS and Linux downloads are archives.</p></article><article><span class="step-number">02</span><h3>Keep your files close</h3><p>Work with local documents. These are early builds, so keep backups of important files while trying them out.</p></article><article><span class="step-number">03</span><h3>Check before opening</h3><p>Packages are unsigned. Your operating system may show a security prompt. Verify the download source and file checksum before running it.</p><a href="{SITE_URL}/dl/SHA256SUMS.txt">View SHA-256 checksums ↗</a></article></div></section>
<section class="wrap section prose"><h2>Prefer to build your own?</h2><p>Each app has its own Rust workspace, with desktop and command-line packages. Platform requirements and build instructions live in the repository.</p><a class="btn ghost" href="{REPO}#building">Build from source ↗</a></section>'''


def build(apps: list[dict], site: Path, catalog: dict) -> None:
    (site / "apps").mkdir(parents=True, exist_ok=True)
    (site / "assets" / "icons").mkdir(parents=True, exist_ok=True)
    for name in ("style.css", "site.js"):
        shutil.copyfile(SOURCE / name, site / "assets" / name)
    for name in ("whiteoffice-mark.svg", "whiteoffice-wordmark.svg"):
        shutil.copyfile(ROOT / "brand" / name, site / "assets" / name)
    for a in apps:
        shutil.copyfile(ROOT / "apps" / a['slug'] / "assets" / "app-icon" / "hicolor" / "256x256" / "apps" / f"io.github.her3f.{a['slug']}.png", site / "assets" / "icons" / f"{a['slug']}.png")
    pages = [("index.html", "White Office — A little more room for your work", home(apps), "Four independent apps for documents, spreadsheets, presentations and PDF. Explore White Office and download builds for Windows, macOS and Linux."),
             ("apps/index.html", "The apps — White Office", '<div class="wrap hero"><p class="eyebrow">A PLACE FOR EVERY IDEA</p><h1>Find your tool.<br><em>Make it yours.</em></h1><p class="lede">Write something worth reading. Make sense of the numbers. Tell a better story. Bring every page together.</p></div><section class="wrap section"><div class="app-grid">' + ''.join(card(a, '../') for a in apps) + '</div></section>', "Meet Nib, Tally, Podium and Sheaf: the four independent White Office applications."),
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
