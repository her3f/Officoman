#!/usr/bin/env python3
"""Generate the White Office website (docs/) and the four app READMEs.

One source of truth: the APPS table below feeds both the site pages and the
per-app README, so they cannot drift apart.
"""
from __future__ import annotations

import html
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "docs"
APPS_DIR = ROOT / "apps"

SITE_URL = "https://officoman.whitebearom.com"
REPO = "https://github.com/her3f/officoman"

APPS = [
    {
        "slug": "nib",
        "name": "Nib",
        "role": "Documents",
        "accent": "#33439B",
        "tagline": "Word processing, without the waiting.",
        "lede": (
            "A full word processor with styles, references, review tools and mail merge — "
            "written from scratch in Rust, native on macOS, Windows, Linux and BSD, and in the browser."
        ),
        "upstream": "WordCraft",
        "features": [
            ("Writing", "IME input, smart quotes, AutoCorrect, list autoformat, regex find and replace."),
            ("Formatting", "Fonts, styles, character and paragraph spacing, tabs with leaders, borders."),
            ("Tables", "Merge and split, banded styles, repeating header rows, sort, formulas, text to table."),
            ("References", "Table of contents, footnotes, citations in APA/MLA/Chicago/IEEE, index."),
            ("Review", "Track changes, margin comments, compare documents, accessibility checker."),
            ("Mailings", "Mail merge from CSV, envelopes and labels."),
        ],
        "formats": ".docx read and write · .doc import · PDF export · .odt, .rtf, .html, .md, .tex, .txt",
    },
    {
        "slug": "tally",
        "name": "Tally",
        "role": "Spreadsheets",
        "accent": "#1F7A6B",
        "tagline": "Numbers that keep up with you.",
        "lede": (
            "A spreadsheet built for real data work: styled tables, totals rows, conditional "
            "formatting, sparklines and live charts, in pure Rust."
        ),
        "upstream": "GridCraft",
        "features": [
            ("Tables", "Styled tables with banded rows, totals rows, filter buttons and data bars."),
            ("Formatting", "Conditional formatting, arrow icon sets, sparklines inside cells."),
            ("Charts", "Column and pie charts that follow the data as it changes."),
            ("Formulas", "A formula engine written in Rust, with the worksheet as a first-class object."),
            ("Files", "Opens and saves .xlsx and imports .xls."),
            ("Automation", "Every action is a command, scriptable from the CLI and driveable over MCP."),
        ],
        "formats": ".xlsx read and write · .xls import",
    },
    {
        "slug": "podium",
        "name": "Podium",
        "role": "Presentations",
        "accent": "#B4502E",
        "tagline": "Build the deck. Then present it.",
        "lede": (
            "Slide masters, layouts, shapes, charts, transitions and animations — with a "
            "full-screen presenter view and PDF export."
        ),
        "upstream": "DeckCraft",
        "features": [
            ("Slides", "Masters, eleven layouts, themes, sections, speaker notes and comments."),
            ("Drawing", "150+ preset shapes, glued connectors, freeform, merge shapes, gradient fills."),
            ("Content", "Pictures, tables, charts, SmartArt, audio and video."),
            ("Presenting", "Transitions including Morph, motion paths, presenter view, pen, rehearse timings."),
            ("Export", "PDF, PNG, JPEG, animated GIF and outlines."),
            ("Automation", "200+ commands, a CLI, a JSON control channel and an MCP server."),
        ],
        "formats": ".pptx read and write · PDF, PNG, JPEG and GIF export",
    },
    {
        "slug": "sheaf",
        "name": "Sheaf",
        "role": "PDF",
        "accent": "#6B4E9E",
        "tagline": "Read it, rearrange it, lock it.",
        "lede": (
            "A PDF workbench: read, search, reorganize, combine, split and protect documents "
            "without handing them to a server."
        ),
        "upstream": "PdfCraft",
        "features": [
            ("Read", "Fast rendering, text selection, search, bookmarks and threaded comments."),
            ("Find", "Search across a document, select and copy text exactly as it is drawn."),
            ("Organize", "Reorder, rotate, delete and insert pages like cards on a table."),
            ("Combine", "Merge and split documents without losing a page or a link."),
            ("Protect", "Open protected documents and respect their permissions."),
            ("Everywhere", "Native on macOS, Windows, Linux and FreeBSD, and in the browser."),
        ],
        "formats": "PDF read and write — no account, no telemetry",
    },
]

CSS = """
:root{
  --ink:#0F1433; --indigo:#33439B; --amber:#F2B33D; --paper:#F7F5EF;
  --muted:#62677A; --line:#E2DFD5; --card:#FFFFFF;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  margin:0;background:var(--paper);color:var(--ink);
  font-family:"Segoe UI",Inter,system-ui,-apple-system,"Noto Sans Arabic",sans-serif;
  line-height:1.65;-webkit-font-smoothing:antialiased;
}
a{color:inherit}
.wrap{max-width:1040px;margin:0 auto;padding:0 28px}
header.site{
  position:sticky;top:0;z-index:20;background:rgba(247,245,239,.86);
  backdrop-filter:blur(12px);border-bottom:1px solid var(--line);
}
header.site .wrap{display:flex;align-items:center;gap:14px;height:64px}
header.site .brand{display:flex;align-items:center;gap:10px;font-weight:700;
  letter-spacing:-.4px;text-decoration:none;font-size:1.02rem}
nav.site{margin-left:auto;display:flex;gap:24px;font-size:.9rem}
nav.site a{text-decoration:none;color:var(--muted)}
nav.site a:hover{color:var(--ink)}

.hero{padding:84px 0 64px}
.hero .eyebrow{font-size:.76rem;letter-spacing:.16em;text-transform:uppercase;
  color:var(--muted);font-weight:700;margin:0 0 18px}
.hero h1{font-size:clamp(2.2rem,5.2vw,3.5rem);line-height:1.08;letter-spacing:-1.6px;margin:0 0 18px}
.hero h1 em{font-style:normal;color:var(--indigo)}
.hero p.lede{font-size:1.12rem;color:var(--muted);max-width:60ch;margin:0 0 28px}
.cta{display:flex;gap:12px;flex-wrap:wrap}
.btn{display:inline-block;padding:11px 22px;border-radius:9px;text-decoration:none;
  font-weight:600;font-size:.93rem;border:1px solid var(--ink);background:var(--ink);color:var(--paper)}
.btn.ghost{background:transparent;color:var(--ink)}

section{padding:56px 0;border-top:1px solid var(--line)}
h2.section{font-size:.76rem;letter-spacing:.16em;text-transform:uppercase;
  color:var(--muted);font-weight:700;margin:0 0 26px}

.grid{display:grid;gap:18px}
.grid.apps{grid-template-columns:repeat(auto-fit,minmax(230px,1fr))}
a.card{display:block;background:var(--card);border:1px solid var(--line);border-radius:16px;
  padding:26px 24px;text-decoration:none;transition:transform .16s ease,box-shadow .16s ease}
a.card:hover{transform:translateY(-3px);box-shadow:0 12px 30px rgba(15,20,51,.09)}
a.card img{width:56px;height:56px;display:block;margin-bottom:16px}
a.card .role{font-size:.72rem;letter-spacing:.13em;text-transform:uppercase;
  color:var(--muted);font-weight:700}
a.card h3{margin:6px 0 8px;font-size:1.28rem;letter-spacing:-.4px}
a.card p{margin:0;color:var(--muted);font-size:.92rem}

.features{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}
.feature{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:20px 22px}
.feature h4{margin:0 0 6px;font-size:.95rem}
.feature p{margin:0;color:var(--muted);font-size:.89rem}

table{width:100%;border-collapse:collapse;font-size:.93rem}
th,td{text-align:left;padding:12px 14px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);font-weight:700}
code{background:#EFEDE5;padding:1px 6px;border-radius:5px;font-size:.87em}

.note{background:#FFF8E8;border:1px solid #EFDBA4;border-radius:12px;padding:18px 22px;
  font-size:.9rem;color:#6B5316}
.note b{color:#4A3A0E}

footer.site{border-top:1px solid var(--line);padding:34px 0 56px;color:var(--muted);font-size:.86rem}
footer.site .wrap{display:flex;gap:18px;flex-wrap:wrap;align-items:center}

td .btn,td .btn.ghost{padding:6px 14px;font-size:.83rem;border-radius:7px;margin-right:6px}
.apphero{padding:64px 0 40px;display:flex;gap:26px;align-items:center;flex-wrap:wrap}
table.platforms th,table.platforms td{padding:18px 14px;vertical-align:top}
table.platforms tbody tr:hover{background:#FCFBF8}
table.platforms td code{font-size:.85rem}
.sub{display:block;font-size:.76rem;color:var(--muted);font-weight:400;margin-top:2px}
.plat-btns{display:flex;gap:6px;flex-wrap:wrap}
.plat-btn{display:inline-block;padding:6px 12px;border-radius:7px;font-size:.79rem;font-weight:600;
  text-decoration:none;border:1px solid var(--ink);background:var(--ink);color:var(--paper);white-space:nowrap}
.plat-btn.ghost{background:transparent;color:var(--ink)}
.plat-btn:hover{opacity:.85}
.plat-sz{display:block;font-size:.68rem;color:var(--muted);margin-top:6px}
.plat-none{color:#C4C0B2}
tr.featured{background:#FCFBF8}
.legend{display:grid;gap:10px;margin-top:24px;font-size:.88rem;color:var(--muted);max-width:80ch}
.legend b{color:var(--ink)}
.apphero img{width:96px;height:96px}
.apphero h1{font-size:clamp(1.9rem,4vw,2.6rem);letter-spacing:-1.1px;margin:0 0 6px}
.apphero .role{font-size:.74rem;letter-spacing:.14em;text-transform:uppercase;
  font-weight:700;color:var(--muted)}
.apphero p{margin:8px 0 0;color:var(--muted);max-width:62ch}
.pill{display:inline-block;font-size:.74rem;font-weight:700;letter-spacing:.06em;
  padding:3px 10px;border-radius:99px;border:1px solid var(--line);background:var(--card);color:var(--muted)}
"""


def page(title: str, body: str, root: str = "", description: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description or 'White Office — an open-source office suite: documents, spreadsheets, presentations and PDF.')}">
<link rel="icon" href="{root}assets/icons/nib.png">
<link rel="stylesheet" href="{root}assets/style.css">
</head>
<body>
<header class="site">
  <div class="wrap">
    <a class="brand" href="{root}index.html">
      <img src="{root}assets/whiteoffice-mark.svg" width="26" height="26" alt="">White Office
    </a>
    <nav class="site">
      <a href="{root}apps/index.html">Apps</a>
      <a href="{root}download.html">Download</a>
      <a href="{root}about.html">About</a>
    </nav>
  </div>
</header>
{body}
<footer class="site">
  <div class="wrap">
    <span>White Office — MIT or Apache-2.0</span>
    <span>·</span>
    <span>Built on the open-source Crafting Apps by the ArtCraft team</span>
    <span>·</span>
    <a href="{root}about.html">Provenance</a>
  </div>
</footer>
</body>
</html>
"""


def app_card(app: dict, root: str = "") -> str:
    return f"""<a class="card" href="{root}apps/{app['slug']}.html">
      <img src="{root}assets/icons/{app['slug']}.png" alt="">
      <div class="role">{app['role']}</div>
      <h3>{app['name']}</h3>
      <p>{html.escape(app['tagline'])}</p>
    </a>"""


def build_pages() -> None:
    (SITE / "apps").mkdir(parents=True, exist_ok=True)
    (SITE / "assets" / "icons").mkdir(parents=True, exist_ok=True)
    (SITE / "assets" / "style.css").write_text(CSS.strip() + "\n", encoding="utf-8")
    (SITE / ".nojekyll").write_text("", encoding="utf-8")

    for svg in ("whiteoffice-mark.svg", "whiteoffice-wordmark.svg"):
        src = ROOT / "brand" / svg
        if src.exists():
            shutil.copy2(src, SITE / "assets" / svg)

    for app in APPS:
        src = APPS_DIR / app["slug"] / "assets" / "app-icon" / "hicolor" / "256x256" / "apps" / f"io.github.her3f.{app['slug']}.png"
        if src.exists():
            shutil.copy2(src, SITE / "assets" / "icons" / f"{app['slug']}.png")

    # ---- landing
    cards = "\n".join(app_card(a) for a in APPS)
    rows = "\n".join(
        f"<tr><td><b>{a['name']}</b></td><td>{a['role']}</td><td>{html.escape(a['tagline'])}</td>"
        f"<td><code>{a['slug']}</code></td></tr>"
        for a in APPS
    )
    body = f"""<main>
<div class="wrap hero">
  <p class="eyebrow">An open-source office suite</p>
  <h1>Four tools.<br>One <em>desk</em>.</h1>
  <p class="lede">Documents, spreadsheets, presentations and PDF. Each one stands on its own,
     each one is native and fast, and together they cover the work you actually do.</p>
  <div class="cta">
    <a class="btn" href="apps/index.html">See the apps</a>
    <a class="btn ghost" href="download.html">Download</a>
  </div>
</div>

<div class="wrap"><section>
  <h2 class="section">The four apps</h2>
  <div class="grid apps">{cards}</div>
</section></div>

<div class="wrap"><section>
  <h2 class="section">What they have in common</h2>
  <div class="features">
    <div class="feature"><h4>Written in Rust</h4><p>One language from the document model to the
      pixel, so the same code runs natively and in the browser.</p></div>
    <div class="feature"><h4>Works offline</h4><p>No account, no telemetry, no server round trip.
      Your documents stay on your disk.</p></div>
    <div class="feature"><h4>Real file formats</h4><p>.docx, .xlsx, .pptx and PDF — files you can
      hand to anyone, not a private format.</p></div>
    <div class="feature"><h4>Scriptable</h4><p>Every action is a command, so the CLI and AI agents
      can drive the same buttons you click.</p></div>
    <div class="feature"><h4>Four platforms</h4><p>macOS, Windows, Linux and BSD, plus a
      WebAssembly build.</p></div>
    <div class="feature"><h4>MIT or Apache-2.0</h4><p>Dual-licensed, forkable, and yours to
      build on.</p></div>
  </div>
</section></div>

<div class="wrap"><section>
  <h2 class="section">At a glance</h2>
  <table>
    <thead><tr><th>App</th><th>Role</th><th>Tagline</th><th>Path</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</section></div>

<div class="wrap"><section>
  <h2 class="section">Where this comes from</h2>
  <div class="note">
    <b>White Office is a fork and rebrand.</b> The four applications are derived from the open-source
    Crafting Apps published by the ArtCraft team under MIT or Apache-2.0, which permits this.
    The licences require attribution, which White Office keeps in full; the ArtCraft names and logos
    are trademarks and are not used here. <a href="about.html">Read the full provenance</a>.
  </div>
</section></div>
</main>"""
    (SITE / "index.html").write_text(
        page("White Office — an open-source office suite", body), encoding="utf-8"
    )

    # ---- apps index
    cards2 = "\n".join(app_card(a, "../") for a in APPS)
    body = f"""<main>
<div class="wrap hero">
  <p class="eyebrow">The suite</p>
  <h1>Four apps,<br>one <em>desk</em>.</h1>
  <p class="lede">Each app is its own program with its own window, its own release and its own
     roadmap. Install the one you need, or all four.</p>
</div>
<div class="wrap"><section>
  <div class="grid apps">{cards2}</div>
</section></div>
</main>"""
    (SITE / "apps" / "index.html").write_text(
        page("Apps — White Office", body, root="../"), encoding="utf-8"
    )

    # ---- per app
    for app in APPS:
        feats = "\n".join(
            f'<div class="feature"><h4>{html.escape(t)}</h4><p>{html.escape(d)}</p></div>'
            for t, d in app["features"]
        )
        others = "\n".join(app_card(a, "../") for a in APPS if a["slug"] != app["slug"])
        body = f"""<main>
<div class="wrap apphero">
  <img src="../assets/icons/{app['slug']}.png" alt="">
  <div>
    <div class="role">{app['role']}</div>
    <h1>{app['name']}</h1>
    <p>{html.escape(app['lede'])}</p>
  </div>
</div>
<div class="wrap"><section style="border-top:none;padding-top:8px">
  <span class="pill">{html.escape(app['formats'])}</span>
</section></div>

<div class="wrap"><section>
  <h2 class="section">What it does</h2>
  <div class="features">{feats}</div>
</section></div>

<div class="wrap"><section>
  <h2 class="section">Status</h2>
  <p style="color:var(--muted);max-width:66ch;margin:0">
    <b>{app['name']}</b> is derived from {app['upstream']}. The source is imported in this
    repository under <code>apps/{app['slug']}</code> and has been rebranded but not yet rebuilt or
    tested here, because no Rust toolchain build has been verified on this tree. Treat it as
    early: build it, run the tests, and expect rough edges.
  </p>
</section></div>

<div class="wrap"><section>
  <h2 class="section">The rest of the suite</h2>
  <div class="grid apps">{others}</div>
</section></div>
</main>"""
        (SITE / "apps" / f"{app['slug']}.html").write_text(
            page(f"{app['name']} — White Office", body, root="../",
                 description=f"{app['name']}: {app['tagline']}"),
            encoding="utf-8",
        )

    # ---- about
    body = f"""<main>
<div class="wrap hero">
  <p class="eyebrow">Provenance and licensing</p>
  <h1>Where this <em>comes from</em>.</h1>
  <p class="lede">White Office is a fork, and it says so plainly. This page records what was
     taken, what was changed, and what the licences require.</p>
</div>

<div class="wrap"><section>
  <h2 class="section">Upstream</h2>
  <table>
    <thead><tr><th>White Office</th><th>Derived from</th><th>Licence</th></tr></thead>
    <tbody>
      <tr><td><b>Nib</b></td><td>WordCraft</td><td>MIT or Apache-2.0</td></tr>
      <tr><td><b>Tally</b></td><td>GridCraft</td><td>MIT or Apache-2.0</td></tr>
      <tr><td><b>Podium</b></td><td>DeckCraft</td><td>MIT or Apache-2.0</td></tr>
      <tr><td><b>Sheaf</b></td><td>PdfCraft</td><td>MIT or Apache-2.0</td></tr>
    </tbody>
  </table>
  <p style="color:var(--muted);max-width:66ch">
    Copyright (c) 2026 ArtCraft Team and the respective Crafting App contributors.
    The full notices are in the repository's <code>NOTICE</code> file.
  </p>
</section></div>

<div class="wrap"><section>
  <h2 class="section">What changed</h2>
  <div class="features">
    <div class="feature"><h4>Names</h4><p>Every product name replaced, including the
      crate names, binaries, window titles and CLI namespaces.</p></div>
    <div class="feature"><h4>Identifiers</h4><p>Bundle identifiers moved from
      <code>ai.storyteller.*</code> to <code>io.github.her3f.*</code> across desktop files,
      Flatpak, AppStream, WiX and macOS packaging.</p></div>
    <div class="feature"><h4>Icons</h4><p>Every app icon redrawn from scratch. The upstream
      icons and brand assets were removed, as their terms require.</p></div>
    <div class="feature"><h4>Links</h4><p>Site, store, Discord, YouTube and social links now
      point at this project.</p></div>
  </div>
</section></div>

<div class="wrap"><section>
  <h2 class="section">Trademarks</h2>
  <div class="note">
    <b>ArtCraft, DeckCraft, GridCraft, PdfCraft, WordCraft</b> and their logos are trademarks of
    the ArtCraft Team. They are not covered by the source licences, and White Office does not use
    them. White Office is not affiliated with, endorsed by, or sponsored by the ArtCraft Team.
    Naming upstream in this page is how the licence asks to be credited — nothing more.
  </div>
</section></div>

<div class="wrap"><section>
  <h2 class="section">Still third-party</h2>
  <p style="color:var(--muted);max-width:66ch">
    The build depends on libraries that live under the same upstream organisation
    (<code>craft-libs</code>, <code>egui</code>, <code>craft-fonts</code>, <code>craft-i18n</code>).
    Those are third-party dependencies, pinned by revision, and their names are left untouched
    on purpose: renaming them would break resolution. Their licences are recorded in each app's
    <code>ATTRIBUTION.md</code>.
  </p>
</section></div>
</main>"""
    (SITE / "about.html").write_text(
        page("About — White Office", body), encoding="utf-8"
    )


def build_downloads() -> None:
    """One table: every app against every platform, built from whatever is in dist/."""
    dist = ROOT / "dist"

    def pick(slug: str, suffix: str):
        return next(iter(sorted(dist.glob(f"{slug}-*-{suffix}"))), None)

    def version_of(slug: str) -> str:
        for suffix in ("windows-x64.msi", "windows-x64-portable.zip",
                       "macos-universal.tar.gz", "linux-x86_64.tar.gz"):
            f = pick(slug, suffix)
            if f:
                return f.name.split(f"{slug}-", 1)[1].split(f"-{suffix}", 1)[0]
        return ""

    def btn(f, label: str, ghost: bool = False) -> str:
        if not f:
            return '<span class="plat-none">—</span>'
        cls = "plat-btn ghost" if ghost else "plat-btn"
        return f'<a class="{cls}" href="/dl/{f.name}">{label}</a>'

    def size(f) -> str:
        return f'<span class="plat-sz">{f.stat().st_size / 1e6:.0f} MB</span>' if f else ""

    rows = []

    l_msi = pick("whiteoffice-launcher", "windows-x64.msi")
    l_zip = pick("whiteoffice-launcher", "windows-x64-portable.zip")
    l_mac = pick("whiteoffice-launcher", "macos-universal.tar.gz")
    l_lin = pick("whiteoffice-launcher", "linux-x86_64.tar.gz")
    if any((l_msi, l_zip, l_mac, l_lin)):
        lv = (l_msi or l_zip or l_mac or l_lin).name.split("whiteoffice-launcher-", 1)[1]
        for suf in ("-windows-x64.msi", "-windows-x64-portable.zip",
                    "-macos-universal.tar.gz", "-linux-x86_64.tar.gz"):
            lv = lv.split(suf, 1)[0]
        rows.append(f"""<tr class="featured">
          <td><b>Launcher</b><span class="sub">installs and updates all four</span></td>
          <td><code>{lv}</code></td>
          <td><div class="plat-btns">{btn(l_msi, ".msi")}{btn(l_zip, ".zip", True)}</div>{size(l_msi or l_zip)}</td>
          <td><div class="plat-btns">{btn(l_mac, ".tar.gz")}</div>{size(l_mac)}</td>
          <td><div class="plat-btns">{btn(l_lin, ".tar.gz")}</div>{size(l_lin)}</td>
        </tr>""")

    for a in APPS:
        slug = a["slug"]
        msi = pick(slug, "windows-x64.msi")
        zp = pick(slug, "windows-x64-portable.zip")
        mac = pick(slug, "macos-universal.tar.gz")
        lin = pick(slug, "linux-x86_64.tar.gz")
        if not any((msi, zp, mac, lin)):
            continue
        rows.append(f"""<tr>
          <td><b>{a["name"]}</b><span class="sub">{a["role"]}</span></td>
          <td><code>{version_of(slug)}</code></td>
          <td><div class="plat-btns">{btn(msi, ".msi")}{btn(zp, ".zip", True)}</div>{size(msi or zp)}</td>
          <td><div class="plat-btns">{btn(mac, ".tar.gz")}</div>{size(mac)}</td>
          <td><div class="plat-btns">{btn(lin, ".tar.gz")}</div>{size(lin)}</td>
        </tr>""")

    if rows:
        table = f"""<table class="platforms">
          <thead><tr>
            <th>App</th><th>Version</th><th>Windows x64</th><th>macOS</th><th>Linux x86_64</th>
          </tr></thead>
          <tbody>{''.join(rows)}</tbody>
        </table>"""
        notes = """<div class="legend">
          <div><b>Windows</b> — <code>.msi</code> installs with a Start Menu entry and file
            associations; <code>.zip</code> is portable, nothing written to the system.</div>
          <div><b>macOS</b> — universal (Apple silicon and Intel). Unpack and run. Unsigned, so
            Gatekeeper asks once: right-click → Open.</div>
          <div><b>Linux</b> — unpack and run. Needs the usual X11/Wayland, GL and ALSA libraries.</div>
        </div>"""
    else:
        table = """<div class="note"><b>No builds yet.</b> Run the packaging scripts and this page
          fills itself in.</div>"""
        notes = ""

    body = f"""<main>
<div class="wrap hero">
  <p class="eyebrow">Download</p>
  <h1>Take them for a <em>spin</em>.</h1>
  <p class="lede">One table, every platform. Pick the build for your machine — each app stands
     on its own, install one or all four.</p>
</div>
<div class="wrap"><section style="border-top:none;padding-top:8px">
  {table}
  {notes}
</section></div>
</main>"""
    (SITE / "download.html").write_text(
        page("Download — White Office", body,
             description="Windows, macOS and Linux builds of the four White Office apps."),
        encoding="utf-8",
    )


def build_readmes() -> None:
    for app in APPS:
        feats = "\n".join(f"| **{t}** | {d} |" for t, d in app["features"])
        md = f"""<p align="center">
  <img src="assets/app-icon/hicolor/128x128/apps/io.github.her3f.{app['slug']}.png" width="88" height="88" alt="{app['name']}">
</p>

<h1 align="center">{app['name']}</h1>

<p align="center"><b>{app['tagline']}</b></p>

<p align="center">Part of <a href="../../">White Office</a>, an open-source office suite.</p>

---

{app['lede']}

## What it does

| Area | Highlights |
|---|---|
{feats}

**Files:** {app['formats']}.

## Building

This app is a Rust workspace. From this directory:

```sh
cargo build --release
cargo test --workspace
```

The desktop app and the CLI are the `{app['slug']}` and `{app['slug']}-cli` packages.
A WebAssembly build of the web front end is published as a separate artifact.

## Status

Early. The source was imported from {app['upstream']} and rebranded, but the rebranded tree has
not been compiled or tested on this machine yet. Build it before trusting it with real work.

## Provenance and licence

This is a modified fork of **{app['upstream']}**, copyright (c) 2026 the ArtCraft Team and the
{app['upstream']} contributors, dual-licensed MIT or Apache-2.0.

Modifications: renamed, rebranded and restructured for White Office, 2026. See the repository
[NOTICE](../../NOTICE) for the full attribution, and [BRAND.md](../../BRAND.md) for what the
rebrand covers.

The ArtCraft, {app['upstream']} and related names and logos are trademarks of the ArtCraft Team
and are not used by this project. White Office is not affiliated with them.

White Office itself is MIT or Apache-2.0, at your option.
"""
        (APPS_DIR / app["slug"] / "README.md").write_text(md, encoding="utf-8")


def main() -> int:
    build_pages()
    build_downloads()
    build_readmes()
    print(f"site:   {SITE.relative_to(ROOT)}/ ({len(list(SITE.rglob('*.html')))} pages)")
    print(f"readmes: {len(APPS)} rewritten")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
