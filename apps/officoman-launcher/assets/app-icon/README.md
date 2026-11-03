# Officoman Launcher app icon

The app icon is the **Officoman "A" mark in blue** (her3f.github.io/officoman's favicon), exactly as supplied in
[`docs/brand/officoman-mark.svg`](../../docs/brand/officoman-mark.svg). Every file in this
directory is rendered from it by `packaging/icons.sh`.

**These files are an Officoman trademark. They are not open source and not covered by Officoman
Launcher's MIT or Apache-2.0 license.** Their terms are in
[`docs/brand/LICENSE-brand.txt`](../../docs/brand/LICENSE-brand.txt): use them only as part of
Officoman Launcher, never redraw, recolor or crop them, and remove them from forks and modified
versions.

## Files

- `officoman-launcher.svg`: a copy of `docs/brand/officoman-mark.svg`; also the hicolor scalable icon.
- `officoman-launcher-1024.png`: 1024 px render, with extra transparent margin for Apple's icon grid.
- `officoman-launcher.icns`: macOS bundle icon (`CFBundleIconFile`).
- `officoman-launcher.ico`: Windows icon, 16–256 px, embedded in the `.exe` by
  `apps/officoman-launcher/build.rs` and used by the MSI.
- `hicolor/<size>/apps/io.github.her3f.officoman-launcher.png` (16–512) and
  `hicolor/scalable/apps/io.github.her3f.officoman-launcher.svg`: Linux icon theme.
- The tray / menu-bar icon is the same mark, rendered into `docs/brand/officoman-mark-black-44.png`
  (macOS template, 22 pt @2x) and `docs/brand/officoman-mark-64.png` (blue; Windows, Linux, FreeBSD).

## Regenerate

Run `packaging/icons.sh` on any OS. It needs `resvg`; the `.ico` and `.icns` are packed by
`cargo xtask ico`. Never edit these files by hand: change the source only if the Officoman Team
supplies a new mark in `docs/brand/`.
