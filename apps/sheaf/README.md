<p align="center">
  <img src="assets/app-icon/hicolor/128x128/apps/io.github.her3f.sheaf.png" width="88" height="88" alt="Sheaf">
</p>

<h1 align="center">Sheaf</h1>

<p align="center"><b>Read it, rearrange it, lock it.</b></p>

<p align="center">Part of <a href="../../">Officoman</a>, an open-source office suite.</p>

---

A PDF workbench: read, search, reorganize, combine, split and protect documents without handing them to a server.

## What it does

| Area | Highlights |
|---|---|
| **Read** | Fast rendering, text selection, search, bookmarks and threaded comments. |
| **Find** | Search across a document, select and copy text exactly as it is drawn. |
| **Organize** | Reorder, rotate, delete and insert pages like cards on a table. |
| **Combine** | Merge and split documents without losing a page or a link. |
| **Protect** | Open protected documents and respect their permissions. |
| **Everywhere** | Native on macOS, Windows, Linux and FreeBSD, and in the browser. |

**Files:** PDF read and write — no account, no telemetry.

## Building

This app is a Rust workspace. From this directory:

```sh
cargo build --release
cargo test --workspace
```

The desktop app and the CLI are the `sheaf` and `sheaf-cli` packages.
A WebAssembly build of the web front end is published as a separate artifact.

## Status

Early. The source was imported from PdfCraft and rebranded, but the rebranded tree has
not been compiled or tested on this machine yet. Build it before trusting it with real work.

## Provenance and licence

This is a modified fork of **PdfCraft**, copyright (c) 2026 the ArtCraft Team and the
PdfCraft contributors, dual-licensed MIT or Apache-2.0.

Modifications: renamed, rebranded and restructured for Officoman, 2026. See the repository
[NOTICE](../../NOTICE) for the full attribution, and [BRAND.md](../../BRAND.md) for what the
rebrand covers.

The ArtCraft, PdfCraft and related names and logos are trademarks of the ArtCraft Team
and are not used by this project. Officoman is not affiliated with them.

Officoman itself is MIT or Apache-2.0, at your option.
