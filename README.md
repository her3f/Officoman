<div align="center">
  <img src="brand/officoman-wordmark.svg" alt="Officoman" width="300">
  <p><strong>Four office tools. One suite.</strong></p>
</div>

---

**Officoman** is a suite of four standalone office applications — documents, spreadsheets,
presentations and PDF — each a full program in its own right, all written in Rust and all
sharing one set of conventions.

> [!IMPORTANT]
> **Status: imported, not yet built.** All four applications are in the repository and fully
> rebranded. The rebranded trees have **not** been compiled or tested yet — build each app
> before trusting it with real work. See [apps/podium](apps/podium) and its siblings.

## The apps

| | App | Role | Files |
|:-:|---|---|---|
| <img src="apps/nib/assets/app-icon/hicolor/64x64/apps/io.github.her3f.nib.png" width="28" alt=""> | **[Nib](apps/nib)** | Word processing and documents | `.docx`, `.doc`, `.odt`, `.rtf`, `.md`, `.tex` |
| <img src="apps/tally/assets/app-icon/hicolor/64x64/apps/io.github.her3f.tally.png" width="28" alt=""> | **[Tally](apps/tally)** | Spreadsheets and data | `.xlsx`, `.xls` |
| <img src="apps/podium/assets/app-icon/hicolor/64x64/apps/io.github.her3f.podium.png" width="28" alt=""> | **[Podium](apps/podium)** | Presentations and slide shows | `.pptx`, PDF/PNG/JPEG export |
| <img src="apps/sheaf/assets/app-icon/hicolor/64x64/apps/io.github.her3f.sheaf.png" width="28" alt=""> | **[Sheaf](apps/sheaf)** | Reading, organizing and protecting PDFs | PDF |

### The launcher

[`apps/officoman-launcher`](apps/officoman-launcher) is the suite's front end: it lists the four
apps, installs the right build for your machine from this repository's releases, and keeps them
up to date.

```sh
cd apps/officoman-launcher
cargo build --release
```

Its catalog is **our four apps only** — the upstream launcher ships seventeen. Each row points at
`github.com/her3f/officoman`, so the four app builds have to be published as release assets named
`<app>-<version>-windows-x64.msi` (or `-portable.zip`) with a `SHA256SUMS.txt` beside them; the
launcher verifies every download against that file before installing it.

Until those releases exist the launcher will show each app as unavailable — that is expected, not
a bug.

## The website

The project site lives in [`docs/`](docs) and is published from that folder with GitHub Pages:

**<https://officoman.whitebearom.com>**

| Page | What it covers |
|---|---|
| [Home](docs/index.html) | What the suite is, the four apps, what they share |
| [Apps](docs/apps/index.html) | One page per app with its features and file formats |
| [About](docs/about.html) | Upstream provenance, what changed, trademark position |

To point GitHub Pages at it: **Settings → Pages → Source: Deploy from a branch →
`main` / `/docs`**.

## Repository layout

```
apps/nib/        Nib — documents          (own Cargo workspace)
apps/tally/      Tally — spreadsheets     (own Cargo workspace)
apps/podium/     Podium — presentations   (own Cargo workspace)
apps/sheaf/      Sheaf — PDF              (own Cargo workspace)
brand/           Officoman marks, palette, proposal page
docs/            The website (GitHub Pages source)
tools/           The scripts that produced this tree
NOTICE           Upstream attribution — required, read it
```

Each app is an independent Rust workspace with its own `Cargo.toml`, its own releases and its
own packaging. Building one does not build the others.

## Building

You need a Rust toolchain (`rustup`, stable):

```sh
cd apps/podium
cargo build --release
cargo test --workspace
```

Repeat for `apps/nib`, `apps/tally`, `apps/sheaf`. The desktop binary and the CLI are the two
`apps/*` packages inside each workspace.

### Windows x64 builds

The Windows builds in `dist/` were produced with the **MinGW-w64** toolchain rather than MSVC,
because the machine that built them has no Visual Studio C++ build tools. Both scripts are in
[`tools/`](tools):

```sh
pwsh -File tools/build_windows.ps1     # cargo build --release, all four apps
pwsh -File tools/package_all.ps1       # portable folder + zip per app, into dist/
```

The zips are self-contained — no runtime DLLs to copy, nothing to install, delete the folder to
uninstall. They are **unsigned**, so Windows SmartScreen warns on first run.

| App | Version | Portable zip |
|---|---|---|
| Nib | 0.15.0 | `dist/Nib-0.15.0-windows-x64-portable.zip` |
| Tally | 0.16.0 | `dist/Tally-0.16.0-windows-x64-portable.zip` |
| Podium | 0.15.0 | `dist/Podium-0.15.0-windows-x64-portable.zip` |
| Sheaf | 0.18.0 | `dist/Sheaf-0.18.0-windows-x64-portable.zip` |

`dist/` is git-ignored; attach those zips to a GitHub release to publish them.

## How this tree was made

The rebrand is scripted, not hand-edited, so it can be re-run or audited:

| Script | What it does |
|---|---|
| [`tools/rebrand.py`](tools/rebrand.py) | Copies each upstream repo into `apps/<name>`, renames every product name, moves bundle identifiers to `io.github.her3f.*`, rewrites links, removes the upstream brand assets |
| [`tools/make_icons.py`](tools/make_icons.py) | Draws every app icon — PNG set, `.ico`, `.icns` and the scalable SVG |
| [`tools/build_docs.py`](tools/build_docs.py) | Generates the website and the four app READMEs from one data table |

Run them in that order to regenerate the tree from `_vendor/`.

## Where this comes from

Officoman is a **fork and rebrand** of the four open-source *Crafting Apps* published by the
[ArtCraft](https://getartcraft.com/) team. Those projects are dual-licensed **MIT or Apache-2.0**,
which permits exactly this: copying, modifying, renaming and redistributing, including
commercially.

In return the licences ask for attribution, which this project keeps in full — see
[NOTICE](NOTICE). The ArtCraft names, the `-Craft` app family and its logos are **trademarks**
and are explicitly *not* licensed; upstream requires forks to remove them, and Officoman does
not use them anywhere. Every upstream icon and brand asset has been deleted and replaced.

Nothing here is affiliated with, endorsed by, or sponsored by the ArtCraft Team.

## License

Dual-licensed under [MIT](LICENSE-MIT) or [Apache-2.0](LICENSE-APACHE), at your option.

Copyright (c) 2026 her3f and the Officoman contributors, and the upstream ArtCraft Team and
Crafting App contributors. Required notices are in [NOTICE](NOTICE).

The Officoman name, wordmark and marks under `brand/` are this project's own.
