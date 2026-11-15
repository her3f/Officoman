"""Validate generated pages and local links without a browser or dependencies."""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class Page(HTMLParser):
    def __init__(self, text: str):
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.errors: list[str] = []
        self.h1 = 0
        self.main = 0
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'h1':
            self.h1 += 1
        if tag == 'main':
            self.main += 1
        if 'id' in attrs:
            if attrs['id'] in self.ids:
                self.errors.append(f"Duplicate id: {attrs['id']}")
            self.ids.add(attrs['id'])
        if tag == 'img' and 'alt' not in attrs:
            self.errors.append('Image without alt text')
        for name in ('href', 'src'):
            if name in attrs:
                self.links.append(attrs[name])
        for name in ('aria-controls', 'aria-labelledby'):
            self.links += ['#' + value for value in attrs.get(name, '').split()]


def validate(site: Path) -> list[str]:
    site = site.resolve()
    pages = {p.resolve(): Page(p.read_text(encoding='utf-8')) for p in site.rglob('*.html')}
    errors = []
    routes = {'index.html', 'download.html', 'apps/index.html',
              'apps/nib.html', 'apps/tally.html', 'apps/podium.html', 'apps/sheaf.html'}
    expected = routes | {'ar/' + route for route in routes}
    actual = {p.relative_to(site).as_posix() for p in pages}
    for path in sorted(expected - actual):
        errors.append(f'Missing page: {path}')
    for path, page in pages.items():
        label = path.relative_to(site)
        errors.extend(f'{label}: {error}' for error in page.errors)
        if page.h1 != 1 or page.main != 1:
            errors.append(f'{label}: expected exactly one h1 and main landmark')
        for link in page.links:
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc:
                if ' ' in link:
                    errors.append(f'{label}: malformed URL {link}')
                continue
            target = (site / parsed.path.lstrip('/') if parsed.path.startswith('/') else path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            if not target.is_relative_to(site):
                errors.append(f'{label}: link outside site: {link}')
                continue
            if target.is_dir():
                target /= 'index.html'
            if not target.is_file():
                errors.append(f'{label}: missing local target {link}')
            elif parsed.fragment and target in pages and unquote(parsed.fragment) not in pages[target].ids:
                errors.append(f'{label}: missing fragment {link}')
    return errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('site', type=Path, nargs='?', default=Path(__file__).resolve().parent.parent / 'docs')
    errors = validate(parser.parse_args().site)
    for error in errors:
        print(error)
    print(f'Site validation: {len(errors)} errors')
    raise SystemExit(bool(errors))
