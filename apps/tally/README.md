<p align="center">
  <img src="assets/app-icon/hicolor/128x128/apps/io.github.her3f.tally.png" width="88" height="88" alt="Tally">
</p>

<h1 align="center">Tally</h1>

<p align="center"><b>Numbers that keep up with you.</b></p>

<p align="center">Part of <a href="../../">White Office</a>, an open-source office suite.</p>

---

A spreadsheet built for real data work: styled tables, totals rows, conditional formatting, sparklines and live charts, in pure Rust.

## What it does

| Area | Highlights |
|---|---|
| **Tables** | Styled tables with banded rows, totals rows, filter buttons and data bars. |
| **Formatting** | Conditional formatting, arrow icon sets, sparklines inside cells. |
| **Charts** | Column and pie charts that follow the data as it changes. |
| **Formulas** | A formula engine written in Rust, with the worksheet as a first-class object. |
| **Files** | Opens and saves .xlsx and imports .xls. |
| **Automation** | Every action is a command, scriptable from the CLI and driveable over MCP. |

**Files:** .xlsx read and write · .xls import.

## Building

This app is a Rust workspace. From this directory:

```sh
cargo build --release
cargo test --workspace
```

The desktop app and the CLI are the `tally` and `tally-cli` packages.
A WebAssembly build of the web front end is published as a separate artifact.

## Status

Early. The source was imported from GridCraft and rebranded, but the rebranded tree has
not been compiled or tested on this machine yet. Build it before trusting it with real work.

## Provenance and licence

This is a modified fork of **GridCraft**, copyright (c) 2026 the ArtCraft Team and the
GridCraft contributors, dual-licensed MIT or Apache-2.0.

Modifications: renamed, rebranded and restructured for White Office, 2026. See the repository
[NOTICE](../../NOTICE) for the full attribution, and [BRAND.md](../../BRAND.md) for what the
rebrand covers.

The ArtCraft, GridCraft and related names and logos are trademarks of the ArtCraft Team
and are not used by this project. White Office is not affiliated with them.

White Office itself is MIT or Apache-2.0, at your option.
