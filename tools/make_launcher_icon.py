#!/usr/bin/env python3
"""Draw the launcher's own icon: the Officoman suite mark (tile, amber fold, O).

Replaces the upstream "A" mark, which is a trademark and must not ship in a fork.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
ICON_DIR = ROOT / "apps" / "officoman-launcher" / "assets" / "app-icon"
SIZES = [16, 24, 32, 48, 64, 128, 256, 512]
BASE = 1024
INSET = 56
RADIUS = 210
AMBER = (242, 179, 61)
TOP = (0x3E, 0x4F, 0xAD)
BOTTOM = (0x0F, 0x14, 0x33)


def lerp(a: int, b: int, t: float) -> int:
    return int(round(a + (b - a) * t))


def gradient(size: int) -> Image.Image:
    img = Image.new("RGB", (1, size))
    px = img.load()
    for y in range(size):
        t = y / max(size - 1, 1)
        px[0, y] = tuple(lerp(TOP[i], BOTTOM[i], t) for i in range(3))
    return img.resize((size, size), Image.Resampling.BILINEAR)


def render() -> Image.Image:
    mask = Image.new("L", (BASE, BASE), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [INSET, INSET, BASE - INSET, BASE - INSET], radius=RADIUS, fill=255
    )

    canvas = Image.new("RGBA", (BASE, BASE), (0, 0, 0, 0))
    canvas.paste(gradient(BASE).convert("RGBA"), (0, 0), mask)

    fold = Image.new("RGBA", (BASE, BASE), (0, 0, 0, 0))
    ImageDraw.Draw(fold).polygon(
        [(BASE - INSET - 300, INSET), (BASE - INSET, INSET), (BASE - INSET, INSET + 300)],
        fill=AMBER + (235,),
    )
    canvas.alpha_composite(Image.composite(fold, Image.new("RGBA", (BASE, BASE)), mask))

    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle([INSET, INSET, BASE - INSET, BASE - INSET], radius=RADIUS,
                        outline=(255, 255, 255, 40), width=3)
    # the O, offset away from the fold
    cx, cy, r, w = 0.452 * BASE, 0.547 * BASE, 0.180 * BASE, 0.081 * BASE
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(247, 245, 239, 255), width=int(w))
    return canvas


SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">
  <title>Officoman Launcher</title>
  <defs>
    <linearGradient id="l" x1="0" y1="0" x2="0.55" y2="1">
      <stop offset="0" stop-color="#3E4FAD"/><stop offset="1" stop-color="#0F1433"/>
    </linearGradient>
    <clipPath id="c"><rect x="4" y="4" width="56" height="56" rx="15"/></clipPath>
  </defs>
  <rect x="4" y="4" width="56" height="56" rx="15" fill="url(#l)"/>
  <g clip-path="url(#c)"><path d="M36 4 H60 V28 Z" fill="#F2B33D" fill-opacity="0.92"/></g>
  <rect x="4.5" y="4.5" width="55" height="55" rx="14.5" fill="none" stroke="#FFFFFF" stroke-opacity="0.16"/>
  <circle cx="29" cy="35" r="11.5" fill="none" stroke="#F7F5EF" stroke-width="5.2"/>
</svg>
"""


def tray_icons() -> None:
    """The tray/menu-bar mark: the same tile with the O cut out, plus a colour copy."""
    brand = ROOT / "apps" / "officoman-launcher" / "docs" / "brand"
    brand.mkdir(parents=True, exist_ok=True)

    # 64 px colour mark
    render().resize((64, 64), Image.Resampling.LANCZOS).save(
        brand / "officoman-mark-64.png", "PNG")

    # 44 px monochrome template: alpha only, the O punched through
    n = 44
    tile = Image.new("L", (n, n), 0)
    ImageDraw.Draw(tile).rounded_rectangle([1, 1, n - 2, n - 2], radius=9, fill=255)
    ring = Image.new("L", (n, n), 0)
    cx, cy, r, w = 0.452 * n, 0.547 * n, 0.180 * n, 0.081 * n
    ImageDraw.Draw(ring).ellipse([cx - r, cy - r, cx + r, cy + r], outline=255, width=max(int(w), 1))
    alpha = Image.composite(tile, Image.new("L", (n, n), 0),
                            Image.eval(ring, lambda v: 255 - v))

    mono = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    mono.putalpha(alpha)
    black = Image.new("RGBA", (n, n), (0, 0, 0, 255))
    black.putalpha(alpha)
    black.save(brand / "officoman-mark-black-44.png", "PNG")
    mono.save(brand / "officoman-mark-black-44-rgba.png", "PNG")


def main() -> int:
    if not ICON_DIR.is_dir():
        print(f"missing {ICON_DIR}")
        return 1
    master = render()
    master.save(ICON_DIR / "officoman-launcher-1024.png", "PNG")

    for n in SIZES:
        d = ICON_DIR / "hicolor" / f"{n}x{n}" / "apps"
        d.mkdir(parents=True, exist_ok=True)
        for old in d.glob("*.png"):
            old.unlink()
        master.resize((n, n), Image.Resampling.LANCZOS).save(
            d / "io.github.her3f.officoman-launcher.png", "PNG")

    s = ICON_DIR / "hicolor" / "scalable" / "apps"
    s.mkdir(parents=True, exist_ok=True)
    for old in s.glob("*.svg"):
        old.unlink()
    (s / "io.github.her3f.officoman-launcher.svg").write_text(SVG, encoding="utf-8")
    (ICON_DIR / "officoman-launcher.svg").write_text(SVG, encoding="utf-8")

    master.save(ICON_DIR / "officoman-launcher.ico", "ICO",
                sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64),
                       (128, 128), (256, 256)])
    try:
        master.save(ICON_DIR / "officoman-launcher.icns", "ICNS")
        note = "icns ok"
    except Exception as exc:                      # noqa: BLE001
        note = f"icns skipped ({exc})"
    print(f"launcher icon: 1024 + {len(SIZES)} sizes + ico + {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
