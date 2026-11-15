"""Shared, deterministic selection of stable release artifacts."""
from pathlib import Path
import re

SUFFIXES = ("windows-x64.msi", "windows-x64-portable.zip",
            "macos-universal.tar.gz", "linux-x86_64.tar.gz")


def version_key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def latest_assets(directory: Path, slug: str) -> tuple[str, dict[str, Path]]:
    """Select one stable version, never mix platforms from different releases."""
    releases: dict[str, dict[str, Path]] = {}
    pattern = re.compile(rf"{re.escape(slug)}-(\d+\.\d+\.\d+)-(.+)")
    for path in directory.glob(f"{slug}-*"):
        match = pattern.fullmatch(path.name)
        if path.is_file() and match and match[2] in SUFFIXES:
            releases.setdefault(match[1], {})[match[2]] = path
    if not releases:
        return "", {}
    version = max(releases, key=version_key)
    return version, releases[version]
