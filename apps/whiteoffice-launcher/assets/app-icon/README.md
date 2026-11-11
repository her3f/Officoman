# White Office Launcher app icon

The app icon is the **White Office "A" mark in blue** (officoman.whitebearom.com's favicon), exactly as supplied in
[`docs/brand/whiteoffice-mark.svg`](../../docs/brand/whiteoffice-mark.svg). Every file in this
directory is rendered from it by `packaging/icons.sh`.

**These files are an White Office trademark. They are not open source and not covered by White Office
Launcher's MIT or Apache-2.0 license.** Their terms are in
[`docs/brand/LICENSE-brand.txt`](../../docs/brand/LICENSE-brand.txt): use them only as part of
White Office Launcher, never redraw, recolor or crop them, and remove them from forks and modified
versions.

## Files

- `whiteoffice-launcher.svg`: a copy of `docs/brand/whiteoffice-mark.svg`; also the hicolor scalable icon.
- `whiteoffice-launcher-1024.png`: 1024 px render, with extra transparent margin for Apple's icon grid.
- `whiteoffice-launcher.icns`: macOS bundle icon (`CFBundleIconFile`).
- `whiteoffice-launcher.ico`: Windows icon, 16–256 px, embedded in the `.exe` by
  `apps/whiteoffice-launcher/build.rs` and used by the MSI.
- `hicolor/<size>/apps/io.github.her3f.whiteoffice-launcher.png` (16–512) and
  `hicolor/scalable/apps/io.github.her3f.whiteoffice-launcher.svg`: Linux icon theme.
- The tray / menu-bar icon is the same mark, rendered into `docs/brand/whiteoffice-mark-black-44.png`
  (macOS template, 22 pt @2x) and `docs/brand/whiteoffice-mark-64.png` (blue; Windows, Linux, FreeBSD).

## Regenerate

Run `packaging/icons.sh` on any OS. It needs `resvg`; the `.ico` and `.icns` are packed by
`cargo xtask ico`. Never edit these files by hand: change the source only if the White Office Team
supplies a new mark in `docs/brand/`.
