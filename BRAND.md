# Brand

Everything in this file is original to Officoman. No ArtCraft asset — logo, wordmark, icon,
name or font — was copied, traced or recoloured.

## The name

**Officoman** · repo `officoman` · words: *Officoman*, *Officoman Nib*, *Officoman Tally*.

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
- The fold and the ring carry the two readings — *page* and *O* — at any size.

Files:

```
brand/officoman-mark.svg        64×64, primary
brand/officoman-wordmark.svg    270×80, horizontal lockup
brand/preview.html              both options, side by side
```

**Known limitation:** the wordmark sets *Officoman* as live text in `Segoe UI`. That is fine
for a README or a GitHub page, but convert it to outlines in a chosen typeface before it goes
on anything printed or shipped.

## Palette

| Name | Hex | Use |
|---|---|---|
| Ink Navy | `#0F1433` | Primary text, dark surfaces |
| Indigo | `#33439B` | Mark gradient top, primary accent |
| Amber | `#F2B33D` | The fold — the one warm accent |
| Paper | `#F7F5EF` | Page background |

## App names

| Role | Name | Note |
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
2. Naming upstream in `NOTICE`, `README` provenance and `LICENSE` is fine and required —
   that is nominative use, describing where the code came from. It is not branding.
3. Never say or imply Officoman is made by, endorsed by, or affiliated with the ArtCraft Team.
4. Do not reuse ArtCraft's app icons, `docs/brand/` assets, bundle identifiers or the
   `ai.storyteller.*` reverse-DNS prefix.

## Import checklist

Work through this per upstream repository as it is imported. Items marked **required** are
licence or trademark obligations, not preferences.

**Remove — required**

- [ ] `docs/brand/` in full (ArtCraft wordmark and logo). Upstream terms state forks and
      modified versions **must** remove these.
- [ ] Every `assets/app-icon/**` icon and splash image.
- [ ] Bundle identifier `ai.storyteller.<app>` → `io.github.her3f.<app>` everywhere:
      Tauri config, `.desktop` files, MSI/WiX, Info.plist, Flatpak manifests, nfpm.
- [ ] Any unlicensed asset paths, if present: `resources/sound/`, `resources/memes/`,
      `resources/skybox/`, `resources/pose/`, `resources/characters_gif/`.

**Rename**

- [ ] Crates: `deckcraft-*` → `podium-*`, `gridcraft-*` → `tally-*`, `pdfcraft-*` → `sheaf-*`,
      `wordcraft-*` → `nib-*`. Watch the many `craft-*` shared crates — those come from
      upstream too and carry the family name.
- [ ] Binaries, CLI names and command namespaces.
- [ ] File extensions if the app registers its own (e.g. `.deckcraft` → `.podium`).
- [ ] UI strings, about boxes, window titles, crash-report text, `Cargo.toml` descriptions
      and `authors` fields.
- [ ] Links: `getartcraft.com`, `discord.gg/artcraft`, YouTube and X handles.
- [ ] Updater endpoints, release URLs and code-signing keys — none of upstream's will work
      for you, and some will actively misroute updates.

**Keep — required**

- [ ] `LICENSE-MIT`, `LICENSE-APACHE` and `NOTICE`, with upstream copyright lines intact.
- [ ] `ATTRIBUTION.md` and every per-asset licence file.
- [ ] A prominent "modified from <upstream>" notice in the header of each changed file
      (Apache-2.0 §4(b)).

**Check**

- [ ] Search the tree for `artcraft`, `craft`, `storytold`, `storyteller` before the first
      public push.
- [ ] Confirm no telemetry or API endpoint still points at upstream infrastructure.
