"""Render Arabic companion pages from the shared English templates, without JS.

All prose must have an explicit translation; new untranslated text fails the build.
Technical names, versions, URLs and package filenames retain their original spelling.
"""
from __future__ import annotations

import html
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import re
from urllib.parse import urlsplit

SITE_URL = "https://officoman.whitebearom.com"
TRANSLATIONS = {
    " ".join(key.split()): value
    for key, value in json.loads((Path(__file__).parent / "site/ar.json").read_text(encoding="utf-8")).items()
}
NAMES = {"Nib", "Tally", "Podium", "Sheaf", "WordCraft", "GridCraft", "DeckCraft", "PdfCraft",
         "Windows", "Windows x64", "macOS", "Linux", "Linux x86_64",
         "ArtCraft, DeckCraft, GridCraft, PdfCraft, WordCraft", ".msi", ".zip", ".tar.gz"}
TECHNICAL = re.compile(r"(?<!\w)\.?[A-Za-z][A-Za-z0-9_./*+-]*(?:[ \t]+[A-Za-z][A-Za-z0-9_./*+-]*)*")
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


def translate(text: str) -> str:
    key = " ".join(text.split())
    if not key:
        return text
    if key in TRANSLATIONS:
        return TRANSLATIONS[key]
    if key in NAMES or re.fullmatch(r"[\d\s.,·—–()]+", key):
        return key
    if re.fullmatch(r"[\d.]+ MB", key):
        return key.removesuffix(" MB") + " ميغابايت"
    for name in ("Nib", "Tally", "Podium", "Sheaf"):
        if key == f"{name} — White Office":
            return f"{name} — وايت أوفيس"
        if key.startswith(f"{name}: "):
            return name + ": " + translate(key[len(name) + 2:])
    match = re.fullmatch(r"is derived from (WordCraft|GridCraft|DeckCraft|PdfCraft)\. The source is imported in this repository under", key)
    if match:
        return f"مشتق من {match[1]}. توجد الشيفرة المصدرية في هذا المستودع ضمن"
    raise ValueError(f"Missing Arabic translation: {key}")


def isolate(text: str) -> str:
    """Isolate Latin names and extensions so RTL punctuation stays readable."""
    parts, end = [], 0
    for match in TECHNICAL.finditer(text):
        token = match[0].rstrip('.')
        punctuation = match[0][len(token):]
        parts.extend((html.escape(text[end:match.start()]), '<bdi dir="ltr">', html.escape(token), '</bdi>', punctuation))
        end = match.end()
    parts.append(html.escape(text[end:]))
    return ''.join(parts)


class LocalizedPage(HTMLParser):
    def __init__(self, lang: str, path: str):
        super().__init__(convert_charrefs=True)
        self.lang = lang
        self.path = path
        self.stack: list[str] = []
        self.output: list[str] = []

    def handle_decl(self, decl):
        self.output.append(f"<!{decl}>")

    def handle_comment(self, data):
        self.output.append(f"<!--{data}-->")

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            attrs.update(lang=self.lang, dir="rtl" if self.lang == "ar" else "ltr")
        if self.lang == "ar":
            if tag == "meta" and attrs.get("name") == "description":
                attrs['content'] = translate(attrs['content'])
            if tag == "code":
                attrs['dir'] = 'ltr'
            for key in ('alt', 'title', 'aria-label'):
                if attrs.get(key):
                    attrs[key] = translate(attrs[key])
            for key in ('src', 'href'):
                url = attrs.get(key, '')
                if url and not urlsplit(url).scheme and not url.startswith(('/', '#')):
                    # Internal HTML routes stay relative to the Arabic tree; assets are shared.
                    if not urlsplit(url).path.endswith('.html'):
                        attrs[key] = '../' + url
        rendered = ''.join(f' {key}' if value is None else f' {key}="{html.escape(value, quote=True)}"' for key, value in attrs.items())
        self.output.append(f'<{tag}{rendered}>')
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag == 'head':
            canonical = SITE_URL + ('/ar/' if self.lang == 'ar' else '/') + self.path
            self.output.append(f'<!-- locale-links --><link rel="canonical" href="{canonical}">\n')
            for lang, prefix in (('en', ''), ('ar', 'ar/'), ('x-default', '')):
                self.output.append(f'<link rel="alternate" hreflang="{lang}" href="{SITE_URL}/{prefix}{self.path}">\n')
            self.output.append('<!-- /locale-links -->')
        if tag == 'nav':
            root = '../' * (len(PurePosixPath(self.path).parts) - 1)
            target = root + ('../' if self.lang == 'ar' else 'ar/') + self.path
            lang, label = ('en', 'English') if self.lang == 'ar' else ('ar', 'العربية')
            self.output.append(f'<!-- locale-links --><a class="language-switch" href="{target}" lang="{lang}" hreflang="{lang}" dir="{"ltr" if lang == "en" else "rtl"}">{label}</a><!-- /locale-links -->')
        self.output.append(f'</{tag}>')
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()

    def handle_data(self, data):
        if self.stack and self.stack[-1] in {'style', 'script'}:
            self.output.append(data)
            return
        if self.lang == 'ar' and data.strip() and 'code' not in self.stack:
            text = translate(data)
            leading = data[:len(data) - len(data.lstrip())]
            trailing = data[len(data.rstrip()):]
            render = html.escape if 'title' in self.stack else isolate
            self.output.append(leading + render(text) + trailing)
        else:
            self.output.append(html.escape(data))


def render(source: str, lang: str, path: str) -> str:
    source = re.sub(r'<!-- locale-links -->.*?<!-- /locale-links -->', '', source, flags=re.S)
    parser = LocalizedPage(lang, path)
    parser.feed(source)
    parser.close()
    return ''.join(parser.output)


def build_locales(site: Path) -> None:
    pages = sorted(p for p in site.rglob('*.html') if 'ar' not in p.relative_to(site).parts)
    # Render everything before writing, so a missing translation cannot leave partial pages.
    rendered = []
    for path in pages:
        relative = path.relative_to(site).as_posix()
        source = path.read_text(encoding='utf-8')
        rendered.append((path, render(source, 'en', relative)))
        rendered.append((site / 'ar' / relative, render(source, 'ar', relative)))
    for path, content in rendered:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
    urls = ''.join(f'<url><loc>{SITE_URL}/{path.relative_to(site).as_posix()}</loc></url>' for path, _ in rendered)
    (site / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + urls + '</urlset>\n', encoding='utf-8')
