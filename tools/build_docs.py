#!/usr/bin/env python3
"""Generate the White Office website (docs/).

The APPS table supplies site content. Release metadata is tracked separately;
refresh it explicitly with --refresh-releases after packaging.
"""
from __future__ import annotations

from site_builder import main

APPS = [
    {
        "slug": "nib",
        "name": "Nib",
        "role": "Documents",
        "accent": "#33439B",
        "tagline": "Word processing, without the waiting.",
        "lede": (
            "A full word processor with styles, references, review tools and mail merge — "
            "written from scratch in Rust, native on macOS, Windows, Linux and BSD, and in the browser."
        ),
        "upstream": "Nib",
        "features": [
            ("Writing", "IME input, smart quotes, AutoCorrect, list autoformat, regex find and replace."),
            ("Formatting", "Fonts, styles, character and paragraph spacing, tabs with leaders, borders."),
            ("Tables", "Merge and split, banded styles, repeating header rows, sort, formulas, text to table."),
            ("References", "Table of contents, footnotes, citations in APA/MLA/Chicago/IEEE, index."),
            ("Review", "Track changes, margin comments, compare documents, accessibility checker."),
            ("Mailings", "Mail merge from CSV, envelopes and labels."),
        ],
        "formats": ".docx read and write · .doc import · PDF export · .odt, .rtf, .html, .md, .tex, .txt",
    },
    {
        "slug": "tally",
        "name": "Tally",
        "role": "Spreadsheets",
        "accent": "#1F7A6B",
        "tagline": "Numbers that keep up with you.",
        "lede": (
            "A spreadsheet built for real data work: styled tables, totals rows, conditional "
            "formatting, sparklines and live charts, in pure Rust."
        ),
        "upstream": "Tally",
        "features": [
            ("Tables", "Styled tables with banded rows, totals rows, filter buttons and data bars."),
            ("Formatting", "Conditional formatting, arrow icon sets, sparklines inside cells."),
            ("Charts", "Column and pie charts that follow the data as it changes."),
            ("Formulas", "A formula engine written in Rust, with the worksheet as a first-class object."),
            ("Files", "Opens and saves .xlsx and imports .xls."),
            ("Automation", "Every action is a command, scriptable from the CLI and driveable over MCP."),
        ],
        "formats": ".xlsx read and write · .xls import",
    },
    {
        "slug": "podium",
        "name": "Podium",
        "role": "Presentations",
        "accent": "#B4502E",
        "tagline": "Build the deck. Then present it.",
        "lede": (
            "Slide masters, layouts, shapes, charts, transitions and animations — with a "
            "full-screen presenter view and PDF export."
        ),
        "upstream": "Podium",
        "features": [
            ("Slides", "Masters, eleven layouts, themes, sections, speaker notes and comments."),
            ("Drawing", "150+ preset shapes, glued connectors, freeform, merge shapes, gradient fills."),
            ("Content", "Pictures, tables, charts, SmartArt, audio and video."),
            ("Presenting", "Transitions including Morph, motion paths, presenter view, pen, rehearse timings."),
            ("Export", "PDF, PNG, JPEG, animated GIF and outlines."),
            ("Automation", "200+ commands, a CLI, a JSON control channel and an MCP server."),
        ],
        "formats": ".pptx read and write · PDF, PNG, JPEG and GIF export",
    },
    {
        "slug": "sheaf",
        "name": "Sheaf",
        "role": "PDF",
        "accent": "#6B4E9E",
        "tagline": "Read it, rearrange it, lock it.",
        "lede": (
            "A PDF workbench: read, search, reorganize, combine, split and protect documents "
            "without handing them to a server."
        ),
        "upstream": "Sheaf",
        "features": [
            ("Read", "Fast rendering, text selection, search, bookmarks and threaded comments."),
            ("Find", "Search across a document, select and copy text exactly as it is drawn."),
            ("Organize", "Reorder, rotate, delete and insert pages like cards on a table."),
            ("Combine", "Merge and split documents without losing a page or a link."),
            ("Protect", "Open protected documents and respect their permissions."),
            ("Everywhere", "Native on macOS, Windows, Linux and FreeBSD, and in the browser."),
        ],
        "formats": "PDF read and write — no account, no telemetry",
    },
    {
        "slug": "courier",
        "name": "Courier",
        "role": "Mail",
        "accent": "#B03E58",
        "tagline": "Every message, where you expect it.",
        "lede": (
            "Mail, calendar, contacts and tasks in one native program: send and receive, "
            "keep folders in step, and read mail without handing it to a web page."
        ),
        "upstream": "Courier",
        "features": [
            ("Mail", "IMAP, SMTP, JMAP and Microsoft Graph; threads, search, rules and signatures."),
            ("Calendar", "Day, week and month views with shared calendars and meeting replies."),
            ("Contacts", "Address books with vCard import and export."),
            ("Tasks", "To-do lists that stay in step with the account."),
            ("Privacy", "Message HTML is read by our own capped engine: no script, no tracking pixel."),
            ("Everywhere", "Native on macOS, Windows, Linux and FreeBSD, and in the browser."),
        ],
        "formats": ".eml and .mbox read and write · .pst import · .ics and .vcf",
    },
]

if __name__ == "__main__":
    raise SystemExit(main(APPS))
