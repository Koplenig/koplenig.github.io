#!/usr/bin/env python3
"""Render the manually maintained bibliography into readable, searchable static HTML."""
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
START = "<!-- BEGIN_GENERATED_PUBLICATIONS -->"
END = "<!-- END_GENERATED_PUBLICATIONS -->"


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


def render(rows: list[dict]) -> str:
    under_review = [p for p in rows if p.get("status", "").strip() == "under_review"]
    published = [p for p in rows if p.get("status", "").strip() != "under_review"]
    sections = []

    # Under Review is a year-like group, directly below the Publications heading.
    if under_review:
        works = "\n".join(publication_html(p) for p in under_review)
        sections.append(
            '<section class="year-group review-year-group" aria-label="Under Review">'
            '<h3>Under Review</h3>'
            f'<div class="year-publications">{works}</div></section>'
        )

    years: dict[str, list[dict]] = {}
    for p in published:
        years.setdefault(p["year"], []).append(p)
    for year in sorted(years, key=int, reverse=True):
        works = "\n".join(publication_html(p) for p in years[year])
        sections.append(
            f'<section class="year-group" aria-label="Publications from {escape(year)}">'
            f'<h3>{escape(year)}</h3><div class="year-publications">{works}</div></section>'
        )
    return "\n".join(sections)


def build(output_dir: Path) -> None:
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError("Publication CSV has no entries")
    if any(key not in rows[0] for key in ("year", "title", "authors", "status")):
        raise ValueError("Publication CSV is missing required fields")
    html = INDEX_PATH.read_text(encoding="utf-8")
    if html.count(START) != 1 or html.count(END) != 1:
        raise ValueError("Publication HTML markers are missing or duplicated")

    prefix, remainder = html.split(START, 1)
    _, suffix = remainder.split(END, 1)
    html = prefix + START + "\n" + render(rows) + "\n" + END + suffix
    count_pattern = r'(<span class="publication-count" id="publication-count" aria-live="polite">).*?(</span>)'
    html, n = re.subn(count_pattern, lambda m: m.group(1) + f"{len(rows)} works" + m.group(2), html, count=1, flags=re.S)
    if n != 1:
        raise ValueError("Missing total publications counter")

    if html.count('<article class="publication">') != len(rows):
        raise ValueError("HTML rendering lost publication entries")
    if html.count('class="pub-links"') != sum(
        bool(p.get("doi") or p.get("publication_url") or p.get("preprint_url") or
             p.get("data_url") or p.get("full_text_url") or p.get("related_url"))
        for p in rows
    ):
        raise ValueError("HTML rendering lost citation link groups")

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "index.html").write_text(html, encoding="utf-8")
    n_review = sum(p.get("status", "").strip() == "under_review" for p in rows)
    print(f"Rendered {len(rows)} entries (including {n_review} under review) to {output_dir / 'index.html'}")


if __name__ == "__main__":
    build(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "_site")
