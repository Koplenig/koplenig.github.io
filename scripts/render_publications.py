#!/usr/bin/env python3
"""Render a browser-independent academic bibliography from the manually edited CSV."""
from __future__ import annotations

import csv
from html import escape
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data/publications_manual.csv"
INDEX_PATH = ROOT / "index.html"

REVIEW_START = "<!-- BEGIN_GENERATED_UNDER_REVIEW -->"
REVIEW_END = "<!-- END_GENERATED_UNDER_REVIEW -->"
PUBLISHED_START = "<!-- BEGIN_GENERATED_PUBLICATIONS -->"
PUBLISHED_END = "<!-- END_GENERATED_PUBLICATIONS -->"


def html_link(label: str, href: str) -> str:
    uri = (href or "").strip()
    parsed = urlsplit(uri)
    if parsed.scheme not in ("https", "http") or not parsed.netloc:
        return ""
    return f'<a href="{escape(uri, quote=True)}" target="_blank" rel="noopener noreferrer">{escape(label)}</a>'


def publication_html(p: dict) -> str:
    primary = p.get("publication_url") or (
        "https://doi.org/" + p["doi"] if p.get("doi") else ""
    )
    title = html_link(p["title"], primary) or escape(p["title"])
    authors = escape(re.sub(r";\s*", "; ", p["authors"]))
    year = escape(p["year"])
    details = (
        f'<p class="pub-details">{escape(p["publication_details"])}</p>'
        if p.get("publication_details") else ""
    )
    links = []
    if p.get("doi"):
        links.append(html_link("DOI ↗", "https://doi.org/" + p["doi"]))
    elif p.get("publication_url"):
        links.append(html_link("Publication ↗", p["publication_url"]))
    for column, label in (
        ("preprint_url", "Preprint ↗"),
        ("data_url", "Data ↗"),
        ("full_text_url", "Full text ↗"),
        ("related_url", (p.get("related_label") or "Related version") + " ↗"),
    ):
        href = p.get(column, "")
        if href and not (column == "full_text_url" and href == p.get("publication_url")):
            links.append(html_link(label, href))
    links_html = (
        '<div class="pub-links">' + " ".join(filter(None, links)) + "</div>"
        if any(links) else ""
    )
    return (
        '<article class="publication">'
        f'<p class="pub-authors">{authors} ({year})</p>'
        f'<h4 class="pub-title">{title}</h4>'
        f'{details}{links_html}'
        '</article>'
    )


def render_review(rows: list[dict]) -> str:
    reviewed = [p for p in rows if p.get("status", "").strip() == "under_review"]
    if not reviewed:
        return ""
    works = "\n".join(publication_html(p) for p in reviewed)
    return '<div class="under-review-group">' + works + '</div>'


def render_published(rows: list[dict]) -> str:
    published = [p for p in rows if p.get("status", "").strip() != "under_review"]
    years: dict[str, list[dict]] = {}
    for p in published:
        years.setdefault(p["year"], []).append(p)
    sections = []
    for year in sorted(years, key=int, reverse=True):
        works = "\n".join(publication_html(p) for p in years[year])
        sections.append(
            f'<section class="year-group" aria-label="Publications from {escape(year)}">'
            f'<h3>{escape(year)}</h3><div class="year-publications">{works}</div></section>'
        )
    return "\n".join(sections)


def replace_generated(html: str, start: str, end: str, content: str) -> str:
    if html.count(start) != 1 or html.count(end) != 1:
        raise ValueError(f"Publication HTML template markers missing or duplicated: {start}")
    prefix, remainder = html.split(start, 1)
    _, suffix = remainder.split(end, 1)
    return prefix + start + "\n" + content + "\n" + end + suffix


def build(output_dir: Path) -> None:
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError("CSV has no publications")
    reviewed = [p for p in rows if p.get("status", "").strip() == "under_review"]
    published = [p for p in rows if p.get("status", "").strip() != "under_review"]

    html = INDEX_PATH.read_text(encoding="utf-8")
    html = replace_generated(html, REVIEW_START, REVIEW_END, render_review(rows))
    html = replace_generated(html, PUBLISHED_START, PUBLISHED_END, render_published(rows))

    counts = [
        ("under-review-count", f"{len(reviewed)} manuscripts"),
        ("publication-count", f"{len(published)} works"),
    ]
    for element_id, content in counts:
        pattern = r'(<span class="publication-count" id="' + element_id + r'" aria-live="polite">).*?(</span>)'
        html, replacements = re.subn(
            pattern, lambda match: match.group(1) + content + match.group(2),
            html, count=1, flags=re.S,
        )
        if replacements != 1:
            raise ValueError(f"Missing count element: {element_id}")

    if html.count('<article class="publication">') != len(rows):
        raise ValueError("HTML rendering lost publication entries")
    if html.count('class="pub-links"') != sum(
        bool(p.get("doi") or p.get("publication_url") or p.get("preprint_url") or
             p.get("data_url") or p.get("full_text_url") or p.get("related_url"))
        for p in rows
    ):
        raise ValueError("HTML rendering lost link groups")

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "index.html").write_text(html, encoding="utf-8")
    print(f"Rendered {len(reviewed)} under-review manuscripts and "
          f"{len(published)} published works to {output_dir / 'index.html'}")


if __name__ == "__main__":
    build(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "_site")
