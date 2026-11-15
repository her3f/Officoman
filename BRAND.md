# Brand

Everything in this file is original to White Office. No ArtCraft asset — logo, wordmark, icon,
name or font — was copied, traced or recoloured.

## The name

**White Office** · repo `whiteoffice` · words: *White Office*, *White Office Nib*, *White Office Tally*.

Why this one:

- **Free.** A search found no software, product, company or package using the name.
- **Coined.** It describes the category without borrowing anyone's family naming pattern.
- **Umbrella-shaped.** It reads as a suite, so four sub-apps sit under it naturally.

### Names considered and rejected

| Name | Why it was dropped |
|---|---|
| **Qirtas** (قرطاس) | An active Arabic publishing platform already ships under this name ([Qirtas App](https://techbullion.com/qirtas-app-unveils-ai-driven-ecosystem-to-modernize-the-4b-arabic-publishing-industry-at-web-summit-qatar-2026/)) — same category, Arabic documents. |
| **Vellum** | Long-established writing application. |
| **Waraq** | Published npm package and an existing GitHub project. |
| **Midad** (مداد) | Two shipping mobile apps already use it. |
| Anything `-craft` | That suffix *is* the ArtCraft family naming. Using it would trade on their trademark pattern even with a different prefix. |

A search finding nothing is **not** trademark clearance. If this ever ships commercially,
run a real clearance and register the mark.

## The mark

A document tile with a folded page corner; the fold doubles as the counter of the **O**.

- Geometric, so it survives at 16 px and in one colour.
- No lettering, so it does not depend on a font being installed.
- The amber fold is the one constant across the suite — every app icon carries it.

```
brand/whiteoffice-mark.svg        64×64, primary
brand/whiteoffice-wordmark.svg    270×80, horizontal lockup
brand/preview.html              both options, side by side
```

**Known limitation:** the wordmark sets *White Office* as live text in `Segoe UI`. That is fine
for a README or a GitHub page, but convert it to outlines in a chosen typeface before it goes
on anything printed or shipped.

## Palette

| Name | Hex | Use |
|---|---|---|
| Ink Navy | `#0F1433` | Primary text, dark surfaces |
| Indigo | `#33439B` | Mark gradient top, primary accent |
| Amber | `#F2B33D` | The fold — the one warm accent |
| Paper | `#F7F5EF` | Page background |

Each app takes one saturated colour so the four are told apart at a glance:

| App | Colour |
|---|---|
| Nib — documents | Indigo `#33439B` |
| Tally — spreadsheets | Teal `#1F7A6B` |
| Podium — presentations | Rust `#B4502E` |
| Sheaf — PDF | Violet `#6B4E9E` |

## App names

| Role | Name | Why |
|---|---|---|
| Documents | **Nib** | The writing end of a pen |
| Spreadsheets | **Tally** | A running count |
| Presentations | **Podium** | Where you stand to present |
| PDF | **Sheaf** | A bundle of loose pages |

An Arabic set exists if the suite is ever aimed at an Arabic-first audience:
**Safha** (صفحة) · **Jadwal** (جدول) · **Ard** (عرض) · **Wathiq** (وثيق).

## House rules

1. Never use *ArtCraft*, *Crafting Apps*, *DeckCraft*, *GridCraft*, *PdfCraft* or *WordCraft*
   in any product-facing string, icon, package name or store listing.
2. Naming upstream in `NOTICE`, `README` provenance and the site's About page is fine and
   required — that is nominative use, describing where the code came from. It is not branding.
3. Never say or imply White Office is made by, endorsed by, or affiliated with the ArtCraft Team.
4. Do not reuse ArtCraft's app icons, `docs/brand/` assets, bundle identifiers or the
   `ai.storyteller.*` reverse-DNS prefix.

## Import record

The four upstream repositories were imported by `tools/rebrand.py` and the result was audited.

**Done**

- [x] `docs/brand/` deleted from all four trees (ArtCraft wordmarks and logos).
- [x] Every app icon deleted and redrawn — PNG set, `.ico`, `.icns`, scalable SVG.
- [x] Bundle identifier `ai.storyteller.*` → `io.github.her3f.*` across desktop files,
      AppStream metainfo, Flatpak manifests, WiX, `Info.plist`, nfpm and `omastore.toml`.
- [x] Product names replaced in every casing that occurs — including the `Pdfcraft*` WiX
      identifiers, `Deckcraft`, and the all-caps constants.
- [x] Crate names, binaries, CLI namespaces and the `repository` field.
- [x] Site, store, Discord, YouTube, X and LinkedIn links now point at this project.
- [x] `LICENSE-MIT`, `LICENSE-APACHE` and `NOTICE` carried over with upstream copyright lines.
- [x] macOS DMG `.DS_Store` layout blobs regenerated, so the mounted volume no longer
      announces the upstream name in Finder.

**Left deliberately**

| Item | Why |
|---|---|
| `storytold/craft-libs`, `storytold/egui`, `storytold/craft-fonts`, `storytold/craft-i18n`, `storytold/winprint.rs` | Third-party git dependencies pinned by revision. Renaming them breaks dependency resolution. They are libraries, not product branding. |
| `craft-*` crate names inside the tree | Internal code identifiers of those dependencies. |
| Historical dev notes in `docs/` that mention sibling Crafting Apps | Records of how the upstream code evolved; they name other projects, they do not brand this one. |
| Test fixture fonts whose internal name table says `DeckCraft Legacy` | Binary `.ttf` fixtures; rewriting a font's name table safely needs a font tool, and they are test-only. |
| `docs/brand/` under `apps/sheaf` | Recreated with **our** mark, because Sheaf's About dialog `include_bytes!`s it. The files are White Office's own artwork, not upstream's. |

## Regenerating

```sh
python tools/rebrand.py       # _vendor/<upstream>  ->  apps/<product>
python tools/scrub_vendor.py  # upstream legal entity + stale attribution rows
python tools/make_icons.py    # draws every icon
python tools/build_docs.py    # website + per-app READMEs
```

`_vendor/` is git-ignored. Re-running the whole chain is idempotent: `apps/<product>` is
deleted and recopied from `_vendor/` each time.

One step is not covered by those three: the macOS DMG layout blob is a binary Finder file, so
`tools/rebrand.py` cannot rewrite it as text. After a re-run, regenerate it per app:

```sh
pip install ds_store==1.3.3 mac_alias==2.2.3
python apps/<app>/packaging/macos/dmg/generate.py   # also needs resvg, for background.tiff
```
