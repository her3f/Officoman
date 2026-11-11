<p align="center">
  <img src="assets/app-icon/hicolor/128x128/apps/io.github.her3f.podium.png" width="88" height="88" alt="Podium">
</p>

<h1 align="center">Podium</h1>

<p align="center"><b>Build the deck. Then present it.</b></p>

<p align="center">Part of <a href="../../">White Office</a>, an open-source office suite.</p>

---

Slide masters, layouts, shapes, charts, transitions and animations — with a full-screen presenter view and PDF export.

## What it does

| Area | Highlights |
|---|---|
| **Slides** | Masters, eleven layouts, themes, sections, speaker notes and comments. |
| **Drawing** | 150+ preset shapes, glued connectors, freeform, merge shapes, gradient fills. |
| **Content** | Pictures, tables, charts, SmartArt, audio and video. |
| **Presenting** | Transitions including Morph, motion paths, presenter view, pen, rehearse timings. |
| **Export** | PDF, PNG, JPEG, animated GIF and outlines. |
| **Automation** | 200+ commands, a CLI, a JSON control channel and an MCP server. |

**Files:** .pptx read and write · PDF, PNG, JPEG and GIF export.

## Building

This app is a Rust workspace. From this directory:

```sh
cargo build --release
cargo test --workspace
```

The desktop app and the CLI are the `podium` and `podium-cli` packages.
A WebAssembly build of the web front end is published as a separate artifact.

## Status

Early. The source was imported from DeckCraft and rebranded, but the rebranded tree has
not been compiled or tested on this machine yet. Build it before trusting it with real work.

## Provenance and licence

This is a modified fork of **DeckCraft**, copyright (c) 2026 the ArtCraft Team and the
DeckCraft contributors, dual-licensed MIT or Apache-2.0.

Modifications: renamed, rebranded and restructured for White Office, 2026. See the repository
[NOTICE](../../NOTICE) for the full attribution, and [BRAND.md](../../BRAND.md) for what the
rebrand covers.

The ArtCraft, DeckCraft and related names and logos are trademarks of the ArtCraft Team
and are not used by this project. White Office is not affiliated with them.

White Office itself is MIT or Apache-2.0, at your option.
