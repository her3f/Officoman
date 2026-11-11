#!/usr/bin/env python3
"""Draw the White Office app icons.

Each app gets the same construction: a rounded tile in its own colour, the amber
folded corner shared by the suite mark, and one bold glyph that survives 16 px.

Writes every size the packaging scripts expect:
  assets/app-icon/<slug>-1024.png
  assets/app-icon/<slug>.ico           (multi-resolution, Windows)
  assets/app-icon/<slug>.icns          (macOS)
  assets/app-icon/hicolor/<N>x<N>/apps/io.github.her3f.<slug>.png
  assets/app-icon/hicolor/scalable/apps/io.github.her3f.<slug>.svg
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
APPS = ROOT / "apps"

SIZES = [16, 24, 32, 48, 64, 128, 256, 512]
BASE = 1024
INSET = 56          # tile margin inside the canvas
RADIUS = 210        # corner radius
AMBER = (242, 179, 61)

APPS_META = {
    "nib":    {"colour": (51, 67, 155)},    # indigo
    "tally":  {"colour": (31, 122, 107)},   # teal
    "podium": {"colour": (180, 80, 46)},    # rust
    "sheaf":  {"colour": (107, 78, 158)},   # violet
}


def lerp(a: int, b: int, t: float) -> int:
    return int(round(a + (b - a) * t))


def gradient(size: int, top: tuple, bottom: tuple) -> Image.Image:
    img = Image.new("RGB", (1, size))
    px = img.load()
    for y in range(size):
        t = y / max(size - 1, 1)
        px[0, y] = tuple(lerp(top[i], bottom[i], t) for i in range(3))
    return img.resize((size, size), Image.Resampling.BILINEAR)


def tile_mask() -> Image.Image:
    mask = Image.new("L", (BASE, BASE), 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle(
        [INSET, INSET, BASE - INSET, BASE - INSET], radius=RADIUS, fill=255
    )
    return mask


def glyph(slug: str, d: ImageDraw.ImageDraw, s: float) -> None:
    """Bold white glyph centred on the tile. `s` is the canvas size in px."""
    white = (255, 255, 255, 245)
    w = max(int(0.040 * s), 2)        # stroke weight, proportional to canvas
    r = int(0.026 * s)                # corner radius of the glyph shapes

    def P(x: float, y: float) -> tuple[float, float]:
        return (x * s, y * s)

    if slug == "nib":                # a sheet with ruled lines
        box = [P(0.30, 0.26), P(0.70, 0.74)]
        d.rounded_rectangle(box, radius=r, outline=white, width=w)
        for i, y in enumerate((0.38, 0.47, 0.56, 0.65)):
            x1 = 0.39
            x2 = 0.61 if i < 3 else 0.52
            d.line([P(x1, y), P(x2, y)], fill=white, width=w)

    elif slug == "tally":            # a grid
        d.rounded_rectangle([P(0.27, 0.27), P(0.73, 0.73)],
                            radius=r, outline=white, width=w)
        d.line([P(0.42, 0.27), P(0.42, 0.73)], fill=white, width=w)
        d.line([P(0.58, 0.27), P(0.58, 0.73)], fill=white, width=w)
        d.line([P(0.27, 0.42), P(0.73, 0.42)], fill=white, width=w)
        d.line([P(0.27, 0.58), P(0.73, 0.58)], fill=white, width=w)

    elif slug == "podium":           # a presentation screen
        d.rounded_rectangle([P(0.25, 0.27), P(0.75, 0.63)],
                            radius=r, outline=white, width=w)
        d.line([P(0.50, 0.63), P(0.50, 0.74)], fill=white, width=w)
        d.line([P(0.38, 0.74), P(0.62, 0.74)], fill=white, width=w)
        for x, h in ((0.35, 0.46), (0.44, 0.39), (0.53, 0.44), (0.62, 0.36)):
            d.line([P(x, h), P(x, 0.54)], fill=white, width=max(int(w * 0.8), 2))

    elif slug == "sheaf":            # a sheaf of loose pages
        w2 = max(int(w * 0.72), 2)
        for x0 in (0.22, 0.41, 0.60):
            d.rounded_rectangle(
                [P(x0, 0.27), P(x0 + 0.18, 0.73)],
                radius=r, outline=white, width=w2,
            )


def render(slug: str) -> Image.Image:
    colour = APPS_META[slug]["colour"]
    top = tuple(min(255, c + 38) for c in colour)
    bottom = tuple(max(0, c - 40) for c in colour)

    canvas = Image.new("RGBA", (BASE, BASE), (0, 0, 0, 0))
    mask = tile_mask()

    tile = gradient(BASE, top, bottom).convert("RGBA")
    canvas.paste(tile, (0, 0), mask)

    # the amber folded corner, shared with the suite mark
    fold = Image.new("RGBA", (BASE, BASE), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fold)
    fd.polygon([(BASE - INSET - 300, INSET), (BASE - INSET, INSET),
                (BASE - INSET, INSET + 300)], fill=AMBER + (235,))
    canvas.alpha_composite(Image.composite(fold, Image.new("RGBA", (BASE, BASE)),
                                           mask))

    ImageDraw.Draw(canvas).rounded_rectangle(
        [INSET, INSET, BASE - INSET, BASE - INSET], radius=RADIUS,
        outline=(255, 255, 255, 40), width=3,
    )
    glyph(slug, ImageDraw.Draw(canvas), BASE)
    return canvas


def svg(slug: str) -> str:
    c = APPS_META[slug]["colour"]
    hexc = "#%02X%02X%02X" % c
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">
  <title>{slug}</title>
  <rect x="3.5" y="3.5" width="57" height="57" rx="13" fill="{hexc}"/>
  <path d="M38 3.5 H60.5 V26 Z" fill="#F2B33D" fill-opacity="0.92"/>
  <rect x="3.5" y="3.5" width="57" height="57" rx="13" fill="none"
        stroke="#FFFFFF" stroke-opacity="0.16"/>
</svg>
"""


def main() -> int:
    for slug in APPS_META:
        icon_dir = APPS / slug / "assets" / "app-icon"
        if not icon_dir.is_dir():
            print(f"missing {icon_dir}")
            continue

        master = render(slug)
        master.save(icon_dir / f"{slug}-1024.png", "PNG")

        for n in SIZES:
            target_dir = icon_dir / "hicolor" / f"{n}x{n}" / "apps"
            target_dir.mkdir(parents=True, exist_ok=True)
            for old_png in target_dir.glob("*.png"):
                old_png.unlink()
            master.resize((n, n), Image.Resampling.LANCZOS).save(
                target_dir / f"io.github.her3f.{slug}.png", "PNG"
            )

        scalable = icon_dir / "hicolor" / "scalable" / "apps"
        scalable.mkdir(parents=True, exist_ok=True)
        for old_svg in scalable.glob("*.svg"):
            old_svg.unlink()
        (scalable / f"io.github.her3f.{slug}.svg").write_text(svg(slug), encoding="utf-8")

        # Windows .ico
        master.save(icon_dir / f"{slug}.ico", "ICO",
                    sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64),
                           (128, 128), (256, 256)])
        # macOS .icns
        try:
            master.save(icon_dir / f"{slug}.icns", "ICNS")
            icns_note = "icns ok"
        except Exception as exc:                      # noqa: BLE001
            icns_note = f"icns skipped ({exc})"

        print(f"{slug:7} 1024 + {len(SIZES)} sizes + ico + {icns_note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
