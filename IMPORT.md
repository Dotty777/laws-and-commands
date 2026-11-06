# Import methodology and coverage

This repository preserves the laws, commands, instructions, and related studies currently available in **Saints.Bible staging**, imported on **6 November 2026**. The authoritative catalogue is [Laws, Commands, and Instructions — The Entire Holy Bible](https://staging-8e0d-waywardnightjars.wpcomstaging.com/instructions/).

The import contains **all 4,440 catalogue records**, organized under the source's **50 topics**, then General or Personal audience, classification, and stable record ID. The category index is in [README.md](README.md). These are overlapping study records, not a deduplicated or certified exhaustive list of biblical commandments.

## Included collections

| Collection | Records |
| --- | ---: |
| Torah requirements | 1,252 |
| Supplemental instructions | 41 |
| Torah source passage groups | 216 |
| Expanded Old Testament passage records | 2,509 |
| Topical studies | 157 |
| Christ studies | 105 |
| Apostolic teachings | 124 |
| Supplemental passage records | 12 |
| Harmony studies | 24 |
| **Total study records** | **4,440** |

The expanded Old Testament collection covers all **43 Old Testament books** currently included by Saints.Bible, including its additional books. The New Testament register provides navigation for all **27 New Testament books**. The repository imports the existing catalogue's records; it does not invent entries for books or passages that the site has not yet indexed.

The older Instructions Index contains only 1,223 Torah requirements. The import uses the current **1,252-requirement** catalogue and retains the old index only as a source snapshot. Its 29 later additions are included.

## Verses, wording, and editorial notes

Each record retains its original identifier, topic, audience note, classification, scope, source link, and every associated Scripture citation. Original research notes and quotations are attached separately. The raw source snapshots remain available for checking the extraction.

The 12 supplemental passage records and 24 Harmony studies omit their topic label in the individual audience cards. They are filed under **Cross-Scripture studies**, matching the overview's explicit count of 34 General and 2 Personal records. Their JSON records retain the empty original topic and explain this mapping.

The catalogue's **Saints Greek-English source wording** is retained from the General and Personal views. Plain-text extraction normalizes whitespace and stores printed verse labels separately; the raw HTML snapshots preserve the display markup. Multiple verse paragraphs remain in the JSON data. This wording is distinct from the Saints Translation reading text. Source review notices and any explicitly missing Greek-English wording remain marked as provided by the catalogue; associated Saints Translation text is kept separately.

The text of associated Scripture references, including comparison passages and passage context, is resolved from the staging site's **live per-book Saints Translation export endpoints**, supplemented by the separate live pages for Susanna, Bel and the Dragon, and continuation blocks in Proverbs 24 and 31 that the book export omits. Published chapter and verse labels are retained, including Greek Psalm numbering. A book's export generation date can precede the import date because the site reuses its cached export when the chapter modification stamp has not changed. The JSON verse index records each export's generation date and source file.

The import preserves both forms of wording; it does not silently replace the catalogue's Greek-English quotations with a different reading. The original research may itself contain earlier wording, which is retained under research notes. Any reference the published export cannot resolve is listed in [unresolved-references.json](data/unresolved-references.json), with its source link intact. No missing text is reconstructed or supplied from an outside translation.

General and Personal are audience categories. The site's Transformed, Fulfilled, Unchanged, Everlasting, historical, covenant-specific, uncertain, and study-context classifications remain separate. Provisional audience assignments and application review notes remain visible. The import adds no theological classifications or claims about universal application.

## Files

- `categories/`: human-readable Markdown, grouped by the source's 50 topics. Larger categories use a short overview and linked reading parts under 220 KB.
- `data/commands.json`: complete category-sorted records, associated passage text, and original research.
- `data/verses.json`: associated Saints Translation verse units and export provenance.
- `data/categories.json`, `data/summary.json`, and `data/validation.json`: category paths, counts, and validation results.
- `data/source-wording-review.json`: the three source notices for missing Greek-English wording; the available associated Saints Translation text remains separately linked.
- `data/audience-records.json`, `data/main-records.json`, and `data/supporting-records.json`: intermediate extractions for reproducibility.
- `data/quoted-verses.json`: quotations retained from the original research pages, including differing wording.
- `source/pages/`: archived WordPress page content and the rendered main catalogue.
- `source/audience/`: every paginated General and Personal catalogue response.
- `source/translation/books/`: the 70 live per-book translation exports used to resolve citations.
- `source/manifest.json`: SHA-256 checksums of the source snapshots.

## Rebuild and verify

Use Python 3.11 or later with `lxml` installed. All commands run from the repository root.

```sh
python scripts/parse_main.py
python scripts/parse_supporting.py
python scripts/parse_audience.py
python scripts/build_catalogue.py
python scripts/validate_catalogue.py
```

The fetch scripts are resumable and preserve already downloaded snapshots. To take a new snapshot, use a separate checkout or archive directory and verify the source counts again; the validation expectations describe the 6 November 2026 catalogue. Fetching performs read-only requests and respects rate-limit backoff.

## Attribution

Source content and wording: **Saints.Bible**. The Saints Translation exports identify their text as **CC BY-SA 4.0**, with the attribution: “Saints Translation, Saints.Bible, CC BY-SA 4.0. Working study edition; independent specialist review pending.” Preserve this attribution, source links, declared numbering, and the [license conditions](https://creativecommons.org/licenses/by-sa/4.0/) when reusing the translation. Other imported research retains its original source provenance; no additional license for that material is asserted here.
