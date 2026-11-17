"""Regression checks for release selection and reproducible website builds."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from build_docs import APPS
from check_site import validate
import make_feed
from release_assets import latest_assets
from site_builder import SOURCE, build, downloads


class ReleaseTests(unittest.TestCase):
    def test_numeric_version_order_and_no_mixed_platforms(self):
        with tempfile.TemporaryDirectory() as directory:
            dist = Path(directory)
            for name in ('nib-0.9.0-windows-x64.msi', 'nib-0.9.0-macos-universal.tar.gz',
                         'nib-0.10.0-linux-x86_64.tar.gz', 'nib-0.10.0-windows-x64-portable.zip',
                         'nib-1.0.0-rc1-windows-x64.msi', 'nib-9.0.0-windows-x64.wixpdb'):
                (dist / name).write_bytes(b'fixture')
            version, assets = latest_assets(dist, 'nib')
            self.assertEqual(version, '0.10.0')
            self.assertEqual(set(assets), {'linux-x86_64.tar.gz', 'windows-x64-portable.zip'})
            with patch.object(make_feed, 'DIST', dist):
                self.assertEqual(make_feed.version_of('nib'), version)
                feed = make_feed.assets_for('nib', 'https://example.com/')
                self.assertEqual(len(feed), 2)
                self.assertTrue(all('0.10.0' in a['name'] for a in feed))
                self.assertTrue(all(len(a['sha256']) == 64 for a in feed))

    def test_directory_with_asset_name_is_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            dist = Path(directory)
            (dist / 'nib-99.0.0-windows-x64.msi').mkdir()
            self.assertEqual(latest_assets(dist, 'nib'), ('', {}))

    def test_non_windows_release_is_supported(self):
        with tempfile.TemporaryDirectory() as directory:
            dist = Path(directory)
            (dist / 'sheaf-1.0.0-linux-x86_64.tar.gz').write_bytes(b'linux')
            with patch.object(make_feed, 'DIST', dist):
                self.assertEqual(make_feed.version_of('sheaf'), '1.0.0')


class SiteTests(unittest.TestCase):
    def test_build_is_reproducible_and_all_local_links_resolve(self):
        catalog = json.loads((SOURCE / 'releases.json').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            build(APPS, site, catalog)
            before = {p.relative_to(site): p.read_bytes() for p in site.rglob('*') if p.is_file()}
            self.assertEqual(validate(site), [])
            build(APPS, site, catalog)
            after = {p.relative_to(site): p.read_bytes() for p in site.rglob('*') if p.is_file()}
            self.assertEqual(before, after)
            for suffix, asset in catalog['nib']['assets'].items():
                self.assertIn('https://whiteoffice.whitebearom.com/dl/' + asset['name'], (site / 'download.html').read_text(encoding='utf-8'))

    def test_empty_catalog_keeps_apps_visible_without_fake_downloads(self):
        result = downloads(APPS, {})
        for app in APPS:
            self.assertIn(f'id="{app["slug"]}"', result)
        self.assertIn('Not available yet', result)
        self.assertNotIn('class="download-link ', result)

    def test_validator_rejects_broken_fragments_and_missing_files(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            build(APPS, site, {})
            path = site / 'index.html'
            path.write_text(path.read_text(encoding='utf-8') + '<a href="apps/nib.html#missing">Broken</a><img src="missing.png" alt="">', encoding='utf-8')
            errors = validate(site)
            self.assertTrue(any('missing fragment' in e for e in errors))
            self.assertTrue(any('missing local target' in e for e in errors))


@unittest.skipUnless(os.name == 'nt' and shutil.which('pwsh'), 'Windows PowerShell integration checks')
class BuildScriptTests(unittest.TestCase):
    def test_native_build_failure_is_logged_and_returns_failure(self):
        with tempfile.TemporaryDirectory(prefix='whiteoffice-build-test-') as directory:
            root = Path(directory)
            (root / 'tools').mkdir()
            (root / 'apps' / 'nib').mkdir(parents=True)
            (root / 'mingw' / 'bin').mkdir(parents=True)
            shutil.copyfile(Path(__file__).parent / 'build_windows.ps1', root / 'tools' / 'build_windows.ps1')
            (root / 'mingw' / 'bin' / 'cargo.cmd').write_text('@echo off\necho simulated build failure 1>&2\nexit /b 7\n')
            result = subprocess.run(['pwsh', '-NoProfile', '-File', str(root / 'tools' / 'build_windows.ps1'),
                                     '-Apps', 'nib', '-Mingw', str(root / 'mingw'), '-TargetDir', str(root / 'target')],
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn('FAILED (exit 7)', result.stdout)
            self.assertIn('simulated build failure', (root / '_build_nib.log').read_text(encoding='utf-8-sig'))

    def test_packaging_stops_before_mutation_when_build_is_missing(self):
        with tempfile.TemporaryDirectory(prefix='whiteoffice-package-test-') as directory:
            root = Path(directory)
            (root / 'tools').mkdir()
            shutil.copyfile(Path(__file__).parent / 'package_all.ps1', root / 'tools' / 'package_all.ps1')
            result = subprocess.run(['pwsh', '-NoProfile', '-File', str(root / 'tools' / 'package_all.ps1'),
                                     '-Apps', 'nib', '-ReleaseDir', str(root / 'missing')],
                                    capture_output=True, text=True, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Missing build', result.stderr)
            self.assertFalse((root / 'dist').exists())


if __name__ == '__main__':
    unittest.main()
