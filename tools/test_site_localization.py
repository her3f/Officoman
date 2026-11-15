"""Check Arabic coverage, mirrored navigation, downloads and repeatable generation."""
from html.parser import HTMLParser
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

import build_docs
from localize_site import build_locales, render, translate


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.elements = []
        self.feed(path.read_text(encoding='utf-8'))

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

    def matching(self, tag, **attrs):
        return [a for t, a in self.elements if t == tag and all(a.get(k) == v for k, v in attrs.items())]


class LocalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory(prefix='whiteoffice-locales-')
        cls.site = Path(cls.directory.name)
        with patch.object(build_docs, 'SITE', cls.site):
            build_docs.build_pages()
            build_docs.build_downloads()
        build_locales(cls.site)

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def test_all_pages_have_arabic_counterparts_and_reciprocal_switches(self):
        english = [p for p in self.site.rglob('*.html') if 'ar' not in p.relative_to(self.site).parts]
        self.assertEqual(len(english), 8)
        self.assertEqual(len(list(self.site.rglob('*.html'))), 16)
        for en in english:
            ar = self.site / 'ar' / en.relative_to(self.site)
            for current, other, lang, direction in ((en, ar, 'en', 'ltr'), (ar, en, 'ar', 'rtl')):
                page = Page(current)
                self.assertEqual(len(page.matching('html', lang=lang, dir=direction)), 1)
                switches = page.matching('a', **{'class': 'language-switch'})
                self.assertEqual(len(switches), 1)
                self.assertEqual((current.parent / switches[0]['href']).resolve(), other.resolve())
                alternatives = page.matching('link', rel='alternate')
                self.assertEqual({a['hreflang'] for a in alternatives}, {'en', 'ar', 'x-default'})
                expected = 'https://officoman.whitebearom.com/' + current.relative_to(self.site).as_posix()
                self.assertEqual(page.matching('link', rel='canonical')[0]['href'], expected)

    def test_local_assets_and_navigation_resolve_and_stay_in_selected_language(self):
        for path in self.site.rglob('*.html'):
            arabic = 'ar' in path.relative_to(self.site).parts
            for tag, attrs in Page(path).elements:
                for key in ('src', 'href'):
                    url = attrs.get(key, '')
                    if not url or urlsplit(url).scheme or url.startswith(('/', '#')):
                        continue
                    target = (path.parent / urlsplit(url).path).resolve()
                    self.assertTrue(target.is_file(), f'{path}: {url}')
                    if tag == 'a' and target.suffix == '.html' and attrs.get('class') != 'language-switch':
                        self.assertEqual('ar' in target.relative_to(self.site).parts, arabic)

    def test_download_targets_and_versions_are_preserved(self):
        def downloads(path):
            return [a['href'] for a in Page(path).matching('a') if a.get('href', '').startswith('/dl/')]
        self.assertEqual(downloads(self.site / 'download.html'), downloads(self.site / 'ar/download.html'))
        self.assertTrue(Page(self.site / 'ar/download.html').matching('code', dir='ltr'))

    def test_generation_is_repeatable_and_sitemap_covers_both_languages(self):
        paths = list(self.site.rglob('*.html')) + [self.site / 'sitemap.xml']
        original = {p: p.read_bytes() for p in paths}
        build_locales(self.site)
        self.assertEqual(original, {p: p.read_bytes() for p in paths})
        sitemap = ET.parse(self.site / 'sitemap.xml')
        self.assertEqual(len(sitemap.getroot()), 16)

    def test_untranslated_new_content_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Missing Arabic translation'):
            translate('A newly added sentence that needs translation.')

    def test_empty_download_state_is_translated(self):
        with tempfile.TemporaryDirectory(prefix='whiteoffice-empty-downloads-') as directory:
            root = Path(directory)
            with patch.object(build_docs, 'SITE', root), patch.object(build_docs, 'ROOT', root):
                build_docs.build_downloads()
            source = (root / 'download.html').read_text(encoding='utf-8')
            arabic = render(source, 'ar', 'download.html')
            self.assertIn('لا تتوفر إصدارات جاهزة بعد.', arabic)
            self.assertNotIn('No builds yet.', arabic)


if __name__ == '__main__':
    unittest.main()
