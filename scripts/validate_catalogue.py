"""Independently audit the finished catalogue against its archived evidence.

Checks source-published totals and category/audience tables, raw audience-card
coverage and quotations, complete research joins, verse text provenance,
reference-resolution exceptions, Markdown destinations, and archive hashes.
No network access or site mutations are performed.
"""
from __future__ import annotations

import collections
import copy
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlparse

from lxml import html

ROOT = Path(__file__).resolve().parents[1]


def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def text(node):
    return re.sub(r"\s+", " ", node.text_content()).strip()


def url_key(value):
    parsed = urlparse(value)
    return unquote(parsed.path).rstrip("/") + "#" + unquote(parsed.fragment).casefold()


def table_counts(tree, anchor):
    target = tree.xpath(f"//*[@id='{anchor}']")[0]
    tables = target.xpath(".//table") if target.tag == "details" else target.xpath("following::table[1]")
    result = {}
    for row in tables[0].xpath("./tbody/tr"):
        cells = [text(cell) for cell in row.xpath("./th|./td")]
        result[cells[0]] = dict(zip(("General", "Personal", "Total"), (int(c.replace(",", "")) for c in cells[1:])))
    return result


def main():
    failures, warnings = [], []

    def check(condition, description, details=None):
        if not condition:
            failures.append({"check": description, "details": details})

    records = read("data/commands.json")
    by_id = {record["id"]: record for record in records}
    check(len(records) == len(by_id) == 4440, "4,440 unique catalogue IDs", len(records))
    overview = read("source/pages/12728-rest.json")
    overview_tree = html.fromstring(overview["content"]["rendered"])
    collection_counts = table_counts(overview_tree, "counts-collections")
    classification_counts = table_counts(overview_tree, "counts-classifications")
    category_counts = table_counts(overview_tree, "instruction-topic-counts")
    for field, expected in (("collection", collection_counts), ("classification", classification_counts), ("category", category_counts)):
        actual = collections.Counter(record[field] for record in records)
        wanted = {label: counts["Total"] for label, counts in expected.items() if label != "Total"}
        check(dict(actual) == wanted, f"Source-published {field} counts", {"actual": dict(actual), "expected": wanted})
        for label, counts in expected.items():
            if label == "Total":
                continue
            audiences = collections.Counter(record["audience"] for record in records if record[field] == label)
            check(all(audiences[a] == counts[a] for a in ("General", "Personal")), f"Source-published {field}/audience counts: {label}", dict(audiences))
    check(collections.Counter(r["audience"] for r in records) == {"General": 3869, "Personal": 571}, "General/Personal totals")
    check(len(set(category_counts) - {"Total"}) == len({r["category"] for r in records}) == 50, "50 source categories")

    # Read the actual rendered cards rather than deriving expected coverage from
    # another generated JSON file. Compare all source quotations independently.
    archived_ids, raw_quote_count = [], 0
    for file in sorted((ROOT / "source/audience").glob("*.json")):
        payload = json.loads(file.read_text(encoding="utf-8-sig"))
        tree = html.fromstring(payload["content"]["rendered"])
        cards = tree.xpath(".//details[contains(concat(' ',normalize-space(@class),' '),' saints-audience-entry ')]")
        for card in cards:
            record_id = card.get("id", "").removeprefix("audience-")
            archived_ids.append(record_id)
            record = by_id.get(record_id)
            check(record is not None, "Archived audience card is present", record_id)
            if record is None:
                continue
            check(record["audience"].casefold() == file.stem.split("-", 1)[0], "Audience preserved from archived view", record_id)
            expected_quotes = []
            for quote in card.xpath("./div[contains(concat(' ',normalize-space(@class),' '),' saints-greek-wording ')]/blockquote"):
                citation = quote.xpath("./cite/a")[0]
                paragraphs = []
                for original in quote.xpath("./p"):
                    paragraph = copy.deepcopy(original)
                    for small in paragraph.xpath(".//small"):
                        small.drop_tree()
                    paragraphs.append(text(paragraph))
                expected_quotes.append((text(citation), url_key(citation.get("href")), "\n".join(paragraphs)))
            raw_quote_count += len(expected_quotes)
            actual_quotes = [(q["reference"], url_key(q["url"]), q["text"]) for q in record.get("verses", [])]
            check(actual_quotes == expected_quotes, "All original Greek-English quotation text and citations preserved", record_id)
            check(bool(expected_quotes), "Greek-English source wording supplied for record", record_id)
            source_links = card.xpath("./p/a[contains(normalize-space(.),'Full research entry')]/@href")
            check(len(source_links) == 1 and url_key(source_links[0]) == url_key(record["source_url"]), "Original research URL preserved", record_id)
            for anchor in card.xpath("./ul/li/a[@href]"):
                check(any(c["reference"] == text(anchor) and url_key(c["url"]) == url_key(anchor.get("href")) for c in record["citations"]), "Every archived associated citation preserved", {"id": record_id, "reference": text(anchor)})
    check(len(archived_ids) == len(set(archived_ids)) == 4440, "Complete nonduplicated raw audience archive", len(archived_ids))
    check(set(archived_ids) == set(by_id), "Final IDs equal raw audience IDs")

    support = read("data/main-records.json") + read("data/supporting-records.json")
    support_by_url = {url_key(r["source_url"]): r for r in support}
    check(len(support) == len(support_by_url) == 4440, "4,440 distinct full-research source entries")
    for record in records:
        expected = support_by_url.get(url_key(record["source_url"]))
        check(expected is not None, "Research merge uses the precise source URL/anchor", record["id"])
        check(record.get("research") == expected, "Complete original research object preserved", record["id"])
        if expected:
            for cite in expected["citations"]:
                check(any(c["reference"] == cite["reference"] and url_key(c["url"]) == url_key(cite["url"]) for c in record["citations"]), "Every research citation preserved", {"id": record["id"], "reference": cite["reference"]})
            for quote in expected.get("verses", []):
                if quote.get("reference") and quote.get("url"):
                    check(any(c["reference"] == quote["reference"] and url_key(c["url"]) == url_key(quote["url"]) for c in record["citations"]), "Every inline research quotation remains associated", record["id"])
    check(read("data/missing-research.json") == [], "No missing research joins")

    # Build an independent text ledger from the raw current book exports and
    # explicit Daniel-addition verse paragraphs. Every emitted unit must equal
    # one of these archived source units; text cannot be reconstructed or split.
    book_files = list((ROOT / "source/translation/books").glob("*.json"))
    check(len(book_files) == 70, "70 current per-book translation archives", len(book_files))
    ledger = {}
    for file in book_files:
        book = json.loads(file.read_text(encoding="utf-8"))
        count = 0
        for chapter in book["chapters"]:
            for verse in chapter["verses"]:
                key = url_key(chapter["url"].split("#")[0] + f'#v{verse["chapter"]}-{verse["verse"]}')
                check(key not in ledger, "No duplicate current translation verse anchors", key)
                ledger[key] = (verse["text"], file.relative_to(ROOT).as_posix())
                count += 1
        check(count == book["verse_count"], "Raw export verse_count equals actual supplied units", book["slug"])
    for name in ("susanna", "bel-and-the-dragon", "proverbs-24-source-block-2", "proverbs-31-source-block-2"):
        file = ROOT / f"source/translation/{name}-page.json"
        if not file.exists():
            check(False, "Current separately paged source addition archived", name)
            continue
        payload = json.loads(file.read_text(encoding="utf-8"))
        tree = html.fromstring(payload["content"])
        for paragraph in tree.xpath(".//p[@id]"):
            if not re.fullmatch(r"v\d+-\d+[a-z]*(?:-\d+[a-z]*)?", paragraph.get("id"), re.I):
                continue
            copied = copy.deepcopy(paragraph)
            for label in copied.xpath("./span[1]"):
                label.drop_tree()
            ledger[url_key(payload["link"].split("#")[0] + "#" + paragraph.get("id"))] = (text(copied), file.relative_to(ROOT).as_posix())
    verse_bank = read("data/verses.json")
    for key, verse in verse_bank.items():
        check(key == url_key(verse["url"]), "Verse-bank key equals its source URL", key)
        check(key in ledger, "Associated verse exists in a current archived source", key)
        if key in ledger:
            check((verse["text"], verse["source_file"]) == ledger[key], "Associated verse text equals its exact current source", key)
        check(bool(verse["text"].strip()), "Associated verse has nonempty wording", key)

    unresolved = read("data/unresolved-references.json")
    unresolved_keys = {(r["id"], r["reference"], url_key(r["url"]), r.get("role", "Related Scripture")) for r in unresolved}
    associated_count = 0
    used_verse_keys = set()
    for record in records:
        citations = {(c["reference"], url_key(c["url"]), c.get("role", "Related Scripture")) for c in record["citations"]}
        passages = {(p["reference"], url_key(p["url"]), p["role"]) for p in record["associated_passages"]}
        check(citations == passages, "Every citation has an associated-passage result", record["id"])
        for passage in record["associated_passages"]:
            associated_count += 1
            check(len(passage["verse_keys"]) == len(passage["verses"]), "Associated passage keys match wording units", record["id"])
            for key, verse in zip(passage["verse_keys"], passage["verses"]):
                used_verse_keys.add(key)
                bank = verse_bank.get(key)
                check(bank is not None and all(verse[k] == bank[k] for k in ("reference", "url", "text")), "Associated passage equals its indexed verse source", {"id": record["id"], "key": key})
            issue_key = (record["id"], passage["reference"], url_key(passage["url"]), passage["role"])
            needs_review = bool(passage.get("resolution_issues")) or not passage["verses"]
            check((issue_key in unresolved_keys) == needs_review, "Partial/empty reference results are explicitly audited", {"id": record["id"], "reference": passage["reference"]})
    check(used_verse_keys == set(verse_bank), "Verse index has no missing or orphaned units")
    if unresolved:
        warnings.append({"check": "Source references needing resolution review", "occurrences": len(unresolved), "audit": "data/unresolved-references.json"})

    category_files = read("data/categories.json")
    check(len(category_files) == 50, "50 category Markdown files indexed")
    file_records = collections.defaultdict(list)
    for record in records:
        file_records[record.get("record_file", record["category_file"])].append(record)
    rendered_ids = []
    for category in category_files:
        file = (ROOT / category["file"]).resolve()
        check(file.is_relative_to(ROOT) and file.is_file(), "Category path points to an existing repository file", category["file"])
        if not file.is_file():
            continue
        body = file.read_text(encoding="utf-8")
        check(body.startswith("# " + category["category"] + "\n"), "Category Markdown title matches source category", category["file"])
        category_ids = []
        parts = category.get("parts", [category["file"]])
        for part in parts:
            part_file = (ROOT / part).resolve()
            check(part_file.is_relative_to(ROOT) and part_file.is_file(), "Category part exists within repository", part)
            if not part_file.is_file():
                continue
            part_body = part_file.read_text(encoding="utf-8")
            actual_ids = re.findall(r'<a id="([^"]+)"></a>', part_body)
            expected_ids = [r["id"] for r in file_records[part]]
            check(collections.Counter(actual_ids) == collections.Counter(expected_ids), "Rendered part contains each assigned record exactly once", part)
            check(len(part_body.encode("utf-8")) <= 220_000, "Category reading file stays within browsing size limit", part)
            category_ids.extend(actual_ids)
            for target in re.findall(r'\]\(([^)]+)\)', part_body):
                if not urlparse(target).scheme and not target.startswith("#"):
                    check((part_file.parent / target.split("#")[0]).resolve().is_file(), "Local Markdown link resolves", {"file": part, "target": target})
        check(len(category_ids) == category["records"], "Category index count equals rendered records", category["file"])
        rendered_ids.extend(category_ids)
        for target in re.findall(r'\]\(([^)]+)\)', body):
            if not urlparse(target).scheme and not target.startswith("#"):
                check((file.parent / target.split("#")[0]).resolve().is_file(), "Category index link resolves", {"file": category["file"], "target": target})
    check(collections.Counter(rendered_ids) == collections.Counter(r["id"] for r in records), "All catalogue records render exactly once across category parts")

    manifest = read("source/manifest.json")
    manifest_files = set()
    for entry in manifest:
        file = (ROOT / entry["file"]).resolve()
        check(file.is_relative_to(ROOT) and file.is_file(), "Archive manifest path exists within repository", entry["file"])
        if file.is_file():
            body = file.read_bytes()
            check(entry["bytes"] == len(body) and entry["sha256"] == hashlib.sha256(body).hexdigest(), "Source archive size/SHA-256 verified", entry["file"])
            manifest_files.add(entry["file"])
    actual_sources = {p.relative_to(ROOT).as_posix() for p in (ROOT / "source").rglob("*") if p.is_file() and p != ROOT / "source/manifest.json"}
    check(actual_sources == manifest_files, "Every source archive has a manifest entry")
    for folder in ("data", "categories", "source"):
        for file in (ROOT / folder).rglob("*"):
            if not file.is_file() or file.suffix not in {".json", ".md", ".html"}:
                continue
            try:
                body = file.read_text(encoding="utf-8-sig")
                check("\ufffd" not in body, "UTF-8 text has no replacement characters", file.relative_to(ROOT).as_posix())
            except UnicodeDecodeError:
                check(False, "File decodes as UTF-8", file.relative_to(ROOT).as_posix())

    summary = {
        "status": "failed" if failures else ("passed_with_source_exceptions" if warnings else "passed"),
        "records": len(records), "categories": len(category_files),
        "raw_audience_cards": len(archived_ids), "raw_source_wording_quotations": raw_quote_count,
        "full_research_entries": len(support), "associated_passage_occurrences": associated_count,
        "associated_unique_verse_units": len(verse_bank), "verified_source_archives": len(manifest_files),
        "failure_count": len(failures), "warning_count": len(warnings),
        "failures": failures, "warnings": warnings,
    }
    (ROOT / "data/validation.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in summary.items() if key not in {"failures", "warnings"}}, indent=2))
    if failures:
        print(json.dumps(failures[:10], ensure_ascii=True, indent=2))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
