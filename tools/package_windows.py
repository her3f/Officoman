#!/usr/bin/env python3
"""Package a built Windows app into a portable folder and a zip.

    python tools/package_windows.py podium [--mingw C:/Users/x/tools/mingw64]

Reads  apps/<slug>/target/x86_64-pc-windows-gnu/release/
Writes dist/<Name>-<version>-windows-x64/  and  dist/<Name>-<version>-windows-x64-portable.zip

The MinGW build needs a few runtime DLLs next to the executable. They are
discovered with ntldd rather than guessed, so the folder is complete.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

NAMES = {"nib": "Nib", "tally": "Tally", "podium": "Podium", "sheaf": "Sheaf"}


def version_of(app_dir: Path) -> str:
    text = (app_dir / "Cargo.toml").read_text(encoding="utf-8")
    m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    return m.group(1) if m else "0.0.0"


def mingw_dlls(exe: Path, mingw: Path) -> list[Path]:
    ntldd = mingw / "bin" / "ntldd.exe"
    if not ntldd.exists():
        print("  ! ntldd not found, skipping runtime DLL scan", file=sys.stderr)
        return []
    out = subprocess.run([str(ntldd), "-R", str(exe)],
                         capture_output=True, text=True, errors="replace").stdout
    found: list[Path] = []
    for line in out.splitlines():
        if "=>" not in line:
            continue
        target = line.split("=>", 1)[1].strip()
        target = target.split(" (")[0].strip()
        p = Path(target)
        try:
            if p.is_file() and p.resolve().is_relative_to(mingw.resolve()):
                found.append(p)
        except (OSError, ValueError):
            continue
    # de-duplicate, keep order
    seen, unique = set(), []
    for p in found:
        if p.name.lower() not in seen:
            seen.add(p.name.lower())
            unique.append(p)
    return unique


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", choices=sorted(NAMES))
    ap.add_argument("--mingw", default=r"C:\Users\Her3f\tools\mingw64")
    ap.add_argument("--release-dir", default="",
                    help="folder holding the built exe; defaults to <app>/target/release")
    args = ap.parse_args()

    slug = args.slug
    name = NAMES[slug]
    app_dir = ROOT / "apps" / slug
    ver = version_of(app_dir)
    rel = (Path(args.release_dir) if args.release_dir
           else app_dir / "target" / "release")

    exe = rel / f"{slug}.exe"
    cli = rel / f"{slug}-cli.exe"
    if not exe.exists():
        print(f"missing build output: {exe}", file=sys.stderr)
        return 1

    out = DIST / f"{name}-{ver}-windows-x64"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    shutil.copy2(exe, out / exe.name)
    if cli.exists():
        shutil.copy2(cli, out / cli.name)
    for extra in ("NOTICE", "LICENSE-MIT", "LICENSE-APACHE", "ATTRIBUTION.md"):
        src = app_dir / extra
        if src.exists():
            shutil.copy2(src, out / extra)
    # license files the Windows installer definition expects beside the binaries
    for extra in (app_dir / "assets" / "app-icon" / "LICENSE-document.txt",):
        if extra.exists():
            shutil.copy2(extra, out / extra.name)

    dlls = mingw_dlls(exe, Path(args.mingw))
    for dll in dlls:
        shutil.copy2(dll, out / dll.name)

    (out / "RUN.txt").write_text(
        f"{name} {ver} — portable Windows build\n"
        "=====================================\n\n"
        f"Double-click {slug}.exe to start {name}.\n"
        f"{slug}-cli.exe is the command-line companion; try `{slug}-cli --version`.\n\n"
        "Nothing is installed and no registry keys are written: delete this folder to remove it.\n\n"
        "This build was produced with the MinGW-w64 toolchain for testing. It is not\n"
        "code-signed, so Windows SmartScreen may warn on first run.\n\n"
        "Licence: MIT or Apache-2.0. See NOTICE for upstream attribution.\n",
        encoding="utf-8",
    )

    zpath = DIST / f"{name}-{ver}-windows-x64-portable.zip"
    if zpath.exists():
        zpath.unlink()
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in sorted(out.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(out.parent))

    digest = hashlib.sha256(zpath.read_bytes()).hexdigest()
    size = zpath.stat().st_size / 1e6
    print(f"{name} {ver}: {out.relative_to(ROOT)}  ({len(dlls)} runtime DLLs)")
    print(f"  {zpath.relative_to(ROOT)}  {size:.1f} MB")
    print(f"  sha256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
