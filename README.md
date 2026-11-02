<div align="center">
  <img src="brand/officoman-wordmark.svg" alt="Officoman" width="300">
  <p><strong>Four office tools. One suite.</strong></p>
</div>

---

**Officoman** is a suite of four standalone office applications — documents, spreadsheets,
presentations and PDF — built on a shared foundation.

> [!IMPORTANT]
> **Status: scaffold.** This repository currently holds the project's identity, licensing and
> layout. The applications have **not** been imported yet. See [BRAND.md](BRAND.md) for the
> naming decisions and the import checklist.

## The apps

| | App | Role | Upstream project it will be built from |
|:-:|---|---|---|
| <span title="documents">📄</span> | **Nib** | Word processing and documents | [WordCraft](https://github.com/storytold/wordcraft) |
| <span title="sheets">▦</span> | **Tally** | Spreadsheets and data | [GridCraft](https://github.com/storytold/gridcraft) |
| <span title="slides">▶</span> | **Podium** | Presentations and slide shows | [DeckCraft](https://github.com/storytold/deckcraft) |
| <span title="pdf">◫</span> | **Sheaf** | Reading, organizing and protecting PDFs | [PdfCraft](https://github.com/storytold/pdfcraft) |

## Where this comes from

Officoman is a **fork and rebrand** of the four open-source *Crafting Apps* published by the
[ArtCraft](https://getartcraft.com/) team. Those projects are dual-licensed **MIT or Apache-2.0**,
which permits exactly this: copying, modifying, renaming and redistributing, including commercially.

In return the licences ask for attribution, which this project keeps in full — see
[NOTICE](NOTICE). The ArtCraft names, the `-Craft` app family and its logos are **trademarks**
and are explicitly *not* licensed; upstream requires forks to remove them, and Officoman does
not use them anywhere.

Nothing here is affiliated with, endorsed by, or sponsored by the ArtCraft Team.

## Status and roadmap

- [x] Identity: name, marks, palette, app names
- [x] Licensing and provenance (`LICENSE-MIT`, `LICENSE-APACHE`, `NOTICE`)
- [ ] Import the four upstream codebases
- [ ] Apply the rebrand checklist in [BRAND.md](BRAND.md#import-checklist)
- [ ] Build and test each app independently
- [ ] Publish first builds

## Building

Each app will be a Rust workspace. You will need a Rust toolchain (**not currently installed
on this machine** — `cargo` is missing):

```sh
# once the Rust toolchain is installed
rustup toolchain install stable
cargo build --release
```

The upstream projects target macOS, Windows, Linux and FreeBSD, with a WebAssembly build of
DeckCraft.

## License

Dual-licensed under [MIT](LICENSE-MIT) or [Apache-2.0](LICENSE-APACHE), at your option.
Copyright (c) 2026 her3f and the Officoman contributors, and the upstream ArtCraft Team and
Crafting App contributors. Required notices are in [NOTICE](NOTICE).

The Officoman name, wordmark and marks under `brand/` are this project's own.
