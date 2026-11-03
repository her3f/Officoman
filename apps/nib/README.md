<p align="center">
  <img src="assets/app-icon/hicolor/128x128/apps/io.github.her3f.nib.png" width="88" height="88" alt="Nib">
</p>

<h1 align="center">Nib</h1>

<p align="center"><b>Word processing, without the waiting.</b></p>

<p align="center">Part of <a href="../../">Officoman</a>, an open-source office suite.</p>

---

A full word processor with styles, references, review tools and mail merge — written from scratch in Rust, native on macOS, Windows, Linux and BSD, and in the browser.

## What it does

| Area | Highlights |
|---|---|
| **Writing** | IME input, smart quotes, AutoCorrect, list autoformat, regex find and replace. |
| **Formatting** | Fonts, styles, character and paragraph spacing, tabs with leaders, borders. |
| **Tables** | Merge and split, banded styles, repeating header rows, sort, formulas, text to table. |
| **References** | Table of contents, footnotes, citations in APA/MLA/Chicago/IEEE, index. |
| **Review** | Track changes, margin comments, compare documents, accessibility checker. |
| **Mailings** | Mail merge from CSV, envelopes and labels. |

**Files:** .docx read and write · .doc import · PDF export · .odt, .rtf, .html, .md, .tex, .txt.

## Building

This app is a Rust workspace. From this directory:

```sh
cargo build --release
cargo test --workspace
```

The desktop app and the CLI are the `nib` and `nib-cli` packages.
A WebAssembly build of the web front end is published as a separate artifact.

## Status

Early. The source was imported from WordCraft and rebranded, but the rebranded tree has
not been compiled or tested on this machine yet. Build it before trusting it with real work.

## Provenance and licence

This is a modified fork of **WordCraft**, copyright (c) 2026 the ArtCraft Team and the
WordCraft contributors, dual-licensed MIT or Apache-2.0.

Modifications: renamed, rebranded and restructured for Officoman, 2026. See the repository
[NOTICE](../../NOTICE) for the full attribution, and [BRAND.md](../../BRAND.md) for what the
rebrand covers.

The ArtCraft, WordCraft and related names and logos are trademarks of the ArtCraft Team
and are not used by this project. Officoman is not affiliated with them.

Officoman itself is MIT or Apache-2.0, at your option.
