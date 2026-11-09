# Import methodology and coverage

## Current catalogue snapshot

The [current GitHub workbook](source/current/Saints-Bible-Instructions-Catalogue-Torah-Law-Followup.xlsx) reflects the [Torah Law follow-up](audit/torah-law/followup.md). Its SHA-256 checksum is `2261581ac9b2b791b9fd84e4cf7258ebde08488673e5b657f8f02817ecec1c47`.

The [preceding workbook](source/current/Saints-Bible-Instructions-Catalogue-Record-Type-Audit.xlsx) was verified against [Saints.Bible production](https://saints.bible/instructions/) and [staging](https://staging-8e0d-waywardnightjars.wpcomstaging.com/instructions/) on **8 November 2026**. The follow-up is a GitHub catalogue revision.

The workbook contains **6,597 study records** (**5,443 General** and **1,154 Personal**) and **1,071 supplementary Scripture links**. The current workbook and JSON include **2,219 records with no matching record in the original archive**. All seven Record types are represented. Study Context identifies material that supplies context, and Mixed identifies passages with more than one substantive form and no single dominant form.

The [current catalogue JSON](data/current/commands.json) and [current summary](data/current/summary.json) are generated from the Catalogue and Scripture Sources sheets. Each current record includes its primary Scripture reference and URL, any additional Scripture references and their notes, and the catalogue's separate type, origin, audience, and application fields. Use `archived_record_id` to look up the matching `id` in [the archival JSON](data/commands.json) for expanded source wording, verse text, and research. That field is null for the 2,219 records added after the archive.

The [current browse index](browse/README.md) provides GitHub reading views [by Bible book](browse/books/README.md), [by record type](browse/record-types/README.md), and [by topic](browse/categories/README.md). All three views are generated from the current JSON and include all 6,597 study records. The book views link to published Scripture and use Saints.Bible catalogue permalinks. The `categories/` directory holds the topical Markdown from the 6 November 2026 archival import.

The workbook’s Merge Index preserves earlier IDs, primary Scripture and original audiences. The [record type ledger](audit/record-types/decisions.json) and the [Torah Law follow-up ledger](audit/torah-law/followup-decisions.json) preserve prior entries and map merged IDs to survivors.

To rebuild the current JSON, summary, and browse pages from the repository root, use Python 3.11 or later. The `--check` commands compare the generated files with the checked-in copies.

```sh
python scripts/build_current_catalogue.py
python scripts/build_torah_law_categories.py
python scripts/build_browse.py
python scripts/build_current_catalogue.py --check
python scripts/build_torah_law_categories.py --check
python scripts/build_browse.py --check
```

## Torah Law categories

The [Torah Law category layer](data/current/torah-law-categories.json) gives each Torah Law record two study labels. **Form** follows the Jewish division of the commandments into positive and negative, with permissions listed separately. **Category** follows the traditional Christian division of the Mosaic law into moral, ceremonial and civil law, with ceremonial laws grouped by area. The [CSV copy](data/current/torah-law-categories.csv) and the counts are generated from the JSON, and the Torah Law browse pages show both labels.

The layer sits beside the catalogue: the workbook, the current catalogue JSON and the site's classification field are unchanged. After editing the JSON, run `scripts/build_torah_law_categories.py` and then `scripts/build_browse.py`. The [category method](audit/torah-law-categories/README.md) gives the definitions and the records flagged for review.

## Archival import of 6 November 2026

The archival collection preserves the laws, commands, instructions, and related studies available in **Saints.Bible staging on 6 November 2026**. Its source page is [Laws, Commands, and Instructions — The Entire Holy Bible](https://staging-8e0d-waywardnightjars.wpcomstaging.com/instructions/).

The import contains **all 4,440 catalogue records**, organized under the source's **50 topics**, then General or Personal audience, classification, and stable record ID. The [archival category index](README.md#archival-import-and-category-index) lists these topics. The totals count overlapping study records.

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

The expanded Old Testament collection covers all **43 Old Testament books** in the Saints.Bible edition. The New Testament register provides navigation for all **27 New Testament books**. The archival collection reproduces the catalogue records present at the time of the import.

The older Instructions Index contains 1,223 Torah requirements. The archival import uses the **1,252-requirement** catalogue available on 6 November and retains the older index as a source snapshot.

## Verses, wording, and editorial notes

Each record retains its original identifier, topic, audience note, classification, scope, source link, and every associated Scripture citation. Original research notes and quotations are attached separately. The raw source snapshots remain available for checking the extraction.

The 12 supplemental passage records and 24 Harmony studies omit their topic label in the individual audience cards. They are filed under **Cross-Scripture studies**, matching the overview's explicit count of 34 General and 2 Personal records. Their JSON records retain the empty original topic and explain this mapping.

The catalogue's **Saints Greek-English source wording** is retained from the General and Personal views. Plain-text extraction normalizes whitespace and stores printed verse labels separately; the raw HTML snapshots preserve the display markup. Multiple verse paragraphs remain in the JSON data. This wording is distinct from the Saints Translation reading text. Source review notices and any explicitly missing Greek-English wording remain marked as provided by the catalogue; associated Saints Translation text is kept separately.

The text of associated Scripture references, including comparison passages and passage context, is resolved from the staging site's **live per-book Saints Translation export endpoints**, supplemented by the separate live pages for Susanna, Bel and the Dragon, and continuation blocks in Proverbs 24 and 31 that the book export omits. Published chapter and verse labels are retained, including Greek Psalm numbering. A book's export generation date can precede the import date because the site reuses its cached export when the chapter modification stamp has not changed. The JSON verse index records each export's generation date and source file.

The import preserves both forms of wording; it does not silently replace the catalogue's Greek-English quotations with a different reading. The original research may itself contain earlier wording, which is retained under research notes. Any reference the published export cannot resolve is listed in [unresolved-references.json](data/unresolved-references.json), with its source link intact. No missing text is reconstructed or supplied from an outside translation.

General and Personal are audience categories. The site's Transformed, Fulfilled, Unchanged, Everlasting, historical, covenant-specific, uncertain, and study-context classifications remain separate. Provisional audience assignments and application review notes remain visible. The import adds no theological classifications or claims about universal application.

## Archival files

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

## Rebuild and verify the archival import

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
