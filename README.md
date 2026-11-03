# Alexander Koplenig — Personal academic website

**Website:** https://koplenig.github.io

A minimal, accessible academic homepage hosted using GitHub Pages. The homepage contains a profile photograph, contact details, institutional affiliation, research interest, and a manually maintained, reverse-chronological publication list.

## Updating the bibliography (manual only)

The **only live publication source** is [`data/publications_manual.csv`](data/publications_manual.csv).

To add or revise a publication directly on GitHub:

1. Open `data/publications_manual.csv` and click the pencil icon (Edit this file).
2. Insert or edit one record. Keep newer publication years above older ones. Within a year, any order is acceptable.
3. Use the existing records as formatting examples. For titles or fields containing commas, wrap the field in double quotes; to include a literal double quote, write it twice.
4. Commit your changes to `main`, or submit a pull request.
5. GitHub Actions will **validate** the CSV, rebuild the static publication entries in the deployed HTML, and publish the resulting page. It will **not** fetch or modify publication data.

CSV columns:

| Column | Description |
| --- | --- |
| `year` | Four-digit publication year (required) |
| `status` | Leave blank for the year-by-year Publications list, or use `under_review` to show an entry at the beginning of the page. |
| `authors` | Full author names separated by semicolons (required) |
| `title` | Publication title (required) |
| `publication_details` | Journal, book, publisher, volume, pages, etc. |
| `doi` | DOI identifier without a URL prefix (if available) |
| `publication_url` | Primary article, book, or repository URL |
| `preprint_url` | Optional preprint version associated with the main publication |
| `data_url` | Optional dataset URL |
| `related_url` | Optional related version, e.g., a conference abstract |
| `related_label` | Text shown for `related_url` |
| `full_text_url` | Optional full-text or PDF link |

`data/publications_ids.csv` is preserved as the **original 77-entry IDS source snapshot**, not as a publication feed. No ORCID or IDS synchronization is configured. Manual editing is intentional.

## Initial curation

The initial live CSV contains **70 works** (66 in Publications and four in **Under Review**) curated from the original **77 IDS records** (as fetched on 3 November 2026). We kept independently citable chapters, software/resources, and other distinct outputs. Seven variant entries were consolidated into their primary versions:

- 2024 preprint of *Does corpus size influence normalised frequencies?* → 2025 journal article (preprint link retained).
- 2024 arXiv version of *Less than one percent of words would be affected by gender-inclusive language in German press texts* → 2024 journal article (preprint link retained).
- 2024 preprint and 2023 conference abstract of *Human languages trade off complexity against efficiency* → 2025 journal article (links retained).
- 2023 online-first entry of *To drop or not to drop?* → 2024 journal issue version (same DOI).
- Duplicate 2020 journal entry of *Tracking and analyzing recent developments in German-language online press* → one entry with the shared DOI.
- 2020 edited-volume reprint of *Studying Lexical Dynamics and Language Change via Generalized Entropies* → 2019 `Entropy` article; 2019 dataset DOI `10.7910/DVN/OP9PRL` retained as a data link. Correct article DOI: `10.3390/e21050464`.

This initial curation is a starting point; publication years and types can be revised manually where the IDS record uses online-first dates or where multiple versions deserve independent treatment.

## Site files

- `index.html`: profile, links, page structure and a static publication snapshot used as a fallback. The deployed HTML bibliography is regenerated from the CSV on every deployment.
- `assets/profile.jpg`: full-frame, proportionally resized version of the user-provided portrait (no cropping).
- `assets/style.css`: mobile-friendly visual styling.
- `assets/site.js`: optional search enhancement; publications are visible even if JavaScript is disabled.
- `data/publications_manual.csv`: **manual bibliography**, the authoritative live source.
- `data/publications_ids.csv`: preserved historical IDS export.
- `scripts/validate_publications.py`: publication data validation.
- `scripts/render_publications.py`: regenerates the deployed static HTML from the manual CSV.
- `.github/workflows/deploy-pages.yml`: deployment only, no publication import.

## Local testing

From the repository root:

```bash
python3 scripts/validate_publications.py
python3 scripts/render_publications.py _site
python3 -m http.server --directory _site 8000
```

Open http://localhost:8000. The generated publication list does not require JavaScript or an in-browser CSV request.

## Publication updates reminder

A ChatGPT reminder is set for the **first Tuesday of every month** (Europe/Berlin), beginning 1 December 2026, to review and manually update the publications.

## Under Review section

To keep a manuscript in the **Under Review** section, set its `status` column to `under_review`. Once published, clear the status, change the year/venue/DOI as needed, and place it within the descending-year order in the CSV.

The homepage is generated as static HTML: all DOI, preprint, data and full-text links remain visible without JavaScript. The deployment action checks that every DOI and preprint link from the CSV appears in the HTML.
