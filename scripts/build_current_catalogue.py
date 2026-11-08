"""Extract the current public catalogue and its native links from the archived workbook."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import posixpath
import re
from urllib.parse import parse_qs, urlsplit
from xml.etree import ElementTree as ET
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
WORKBOOK_NAME = "Saints-Bible-Instructions-Catalogue-Complete-Record-Types.xlsx"
WORKBOOK_PATH = f"source/current/{WORKBOOK_NAME}"
WORKBOOK_SHA256 = "801c93948bdcf13f65c54fe54676fd4a04c4a49b71fab8b0a5ab468077e2b098"
LIVE_PATH = f"/wp-content/uploads/2026/11/{WORKBOOK_NAME}"
ARCHIVE = "data/commands.json"
RECORD_COUNT = 4999
ARCHIVE_COUNT = 4440
SOURCE_COUNT = 269
X = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
P = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"x": X}

CATALOGUE_COLUMNS = (
    ("Record ID", "id"), ("Scripture", "reference"), ("Study record", "title"),
    ("Study placement", "study_placement"), ("Mosaic type", "mosaic_type"),
    ("Original audience or recipient", "original_audience_or_recipient"),
    ("Audience", "audience"), ("Origin", "origin"), ("Collection", "collection"),
    ("Topic", "topic"), ("Classification", "classification"), ("Bible book", "book"),
    ("Testament", "testament"), ("Audience review", "audience_review"),
    ("Catalogue audience", "catalogue_audience"), ("Context note", "context_note"),
    ("Citation basis", "citation_basis"), ("Origin basis", "origin_basis"),
    ("Mosaic context", "mosaic_context"), ("Mosaic review note", "mosaic_review_note"),
    ("Record type", "record_type"), ("Speaker or source", "speaker_or_source"),
    ("Original audience (audit)", "original_audience_audit"),
    ("Additional Scripture", "additional_scripture_display"),
)
SOURCE_HEADERS = ("Record ID", "Scripture", "Study record", "Context for this source")
MOSAIC_TYPES = {"Law", "Command", "Commission", "Instruction", "Wisdom"}
RECORD_TYPES = MOSAIC_TYPES | {"Mixed", "Study Context"}
ORIGINS = {"Heavenly (God-given)", "Earthly (Man-made)", "Context only", "Mixed origins", "Origin under review"}
CITATION_BASES = {"Source", "Passage context", "Related teaching / comparison"}
REQUIRED_FIELDS = {
    "id", "reference", "title", "study_placement", "audience", "origin", "collection",
    "classification", "book", "testament", "audience_review", "catalogue_audience",
    "citation_basis", "origin_basis", "record_type",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def relationships(workbook: ZipFile, part: str) -> dict:
    folder, name = posixpath.split(part)
    xml_path = posixpath.join(folder, "_rels", name + ".rels")
    root = ET.fromstring(workbook.read(xml_path))
    entries = root.findall(f"{{{P}}}Relationship")
    index = {entry.attrib["Id"]: entry.attrib for entry in entries}
    require(len(index) == len(entries), f"Duplicate relationship in {part}")
    return index


def sheet_parts(workbook: ZipFile) -> dict[str, str]:
    root = ET.fromstring(workbook.read("xl/workbook.xml"))
    rels = relationships(workbook, "xl/workbook.xml")
    parts = {}
    for sheet in root.findall("x:sheets/x:sheet", NS):
        rel = rels[sheet.attrib[f"{{{R}}}id"]]
        target = rel["Target"]
        part = posixpath.normpath(target.lstrip("/") if target.startswith("/") else "xl/" + target)
        require(rel["Type"] == R + "/worksheet" and part.startswith("xl/worksheets/"), f"Unexpected worksheet part: {part}")
        name = sheet.attrib["name"]
        require(name not in parts, f"Duplicate worksheet: {name}")
        parts[name] = part
    return parts


def sheet_data(workbook: ZipFile, part: str, strings: list[str], headers: tuple[str, ...], count: int) -> tuple[dict, dict]:
    root = ET.fromstring(workbook.read(part))
    rows = {}
    for row in root.findall("x:sheetData/x:row", NS):
        number = int(row.attrib["r"])
        if number < 7:
            continue
        require(number not in rows, f"Duplicate row {number} in {part}")
        values = {}
        for cell in row.findall("x:c", NS):
            coordinate = cell.attrib["r"]
            match = re.fullmatch(r"([A-Z]+)([0-9]+)", coordinate)
            require(match is not None and int(match[2]) == number, f"Unexpected cell coordinate {coordinate}")
            col = match[1]
            require(col not in values and cell.find("x:f", NS) is None, f"Duplicate or formula cell {coordinate}")
            value = cell.findtext("x:v", namespaces=NS) or ""
            kind = cell.get("t")
            if kind == "s":
                value = strings[int(value)]
            elif kind == "inlineStr":
                value = "".join(t.text or "" for t in cell.findall("x:is//x:t", NS))
            else:
                require(kind in (None, "str"), f"Unexpected cell type at {coordinate}")
            values[col] = value
        rows[number] = values

    columns = [chr(ord("A") + offset) for offset in range(len(headers))]
    require(set(rows) == set(range(7, count + 8)), f"Unexpected row count in {part}")
    header_row = rows.pop(7)
    require(tuple(header_row.get(column) for column in columns) == headers, f"Unexpected headers in {part}")
    require(all(set(values) <= set(columns) for values in rows.values()), f"Unexpected columns in {part}")
    values = {number: [rows[number].get(column, "") for column in columns] for number in range(8, count + 8)}

    rels = relationships(workbook, part)
    links = {}
    for link in root.findall("x:hyperlinks/x:hyperlink", NS):
        cell = link.attrib["ref"]
        rid = link.get(f"{{{R}}}id")
        location = link.get("location")
        require(cell not in links and bool(rid) != bool(location), f"Invalid hyperlink at {cell} in {part}")
        if rid:
            rel = rels[rid]
            require(rel["Type"] == R + "/hyperlink" and rel.get("TargetMode") == "External", f"Invalid external link at {cell}")
            links[cell] = ("external", rel["Target"])
        else:
            links[cell] = ("internal", location)
    return values, links


def external_link(links: dict, cell: str, prefix: str) -> str:
    kind, url = links[cell]
    target = urlsplit(url)
    require(kind == "external" and target.scheme == "https" and target.netloc == "saints.bible" and
            target.path.startswith(prefix) and bool(target.fragment), f"Unexpected link at {cell}: {url}")
    if prefix == "/bible/":
        require(re.fullmatch(r"v\d+-\d+[a-z]*", target.fragment) is not None and not target.query, f"Invalid Scripture anchor: {url}")
    return url


def extract(workbook_path: Path, archive_ids: set[str], books: list[str]) -> list[dict]:
    with ZipFile(workbook_path) as workbook:
        require(workbook.testzip() is None, "Workbook ZIP integrity check failed")
        shared = ET.fromstring(workbook.read("xl/sharedStrings.xml"))
        strings = ["".join(t.text or "" for t in item.findall(".//x:t", NS)) for item in shared]
        parts = sheet_parts(workbook)
        require(set(parts) == {"Catalogue", "Scripture Sources"}, "Unexpected workbook sheets")
        cat_values, cat_links = sheet_data(workbook, parts["Catalogue"], strings, tuple(h for h, _ in CATALOGUE_COLUMNS), RECORD_COUNT)
        source_values, source_links = sheet_data(workbook, parts["Scripture Sources"], strings, SOURCE_HEADERS, SOURCE_COUNT)

    records = []
    catalogue_rows = {}
    display_refs = {}
    for number, values in cat_values.items():
        record = dict(zip((key for _, key in CATALOGUE_COLUMNS), values))
        record_id = record["id"]
        require(record_id not in catalogue_rows, f"Duplicate record ID {record_id}")
        missing = sorted(key for key in REQUIRED_FIELDS if not record[key].strip())
        require(not missing, f"Missing fields for {record_id}: {', '.join(missing)}")
        require(record["record_type"] in RECORD_TYPES and record["origin"] in ORIGINS and
                record["citation_basis"] in CITATION_BASES and record["audience"] in {"General", "Personal"}, f"Unexpected classification for {record_id}")
        if record["mosaic_type"]:
            require(record["mosaic_type"] in MOSAIC_TYPES and record["mosaic_type"] == record["record_type"] and
                    bool(record["original_audience_or_recipient"]), f"Inconsistent Mosaic typing for {record_id}")
        catalogue_rows[record_id] = number
        display_refs[record_id] = record.pop("additional_scripture_display")
        record["catalogue_url"] = external_link(cat_links, f"A{number}", "/instructions/")
        require(parse_qs(urlsplit(record["catalogue_url"]).query).get("instruction_id") == [record_id], f"Catalogue URL ID differs for {record_id}")
        record["scripture_url"] = external_link(cat_links, f"B{number}", "/bible/")
        record["additional_scripture"] = []
        record["archived_record_id"] = record_id if record_id in archive_ids else None
        records.append(record)

    records_by_id = {record["id"]: record for record in records}
    require(archive_ids <= records_by_id.keys(), "At least one original archive record is missing from the current workbook")
    require(list(dict.fromkeys(record["book"] for record in records)) == books, "Workbook canon coverage or order differs from the 70-book register")
    testament_by_book = {book: "Old" if index < 43 else "New" for index, book in enumerate(books)}
    require(all(record["testament"] == testament_by_book[record["book"]] for record in records), "Workbook testament labels disagree with the register")

    indexes_by_id = defaultdict(list)
    seen_sources = set()
    for number, (record_id, reference, title, context_note) in source_values.items():
        require(record_id in records_by_id and bool(reference.strip()), f"Invalid supporting source at row {number}")
        record = records_by_id[record_id]
        require(title == record["title"], f"Supporting source title differs for {record_id}")
        require(source_links.get(f"A{number}") == ("internal", f"Catalogue!A{catalogue_rows[record_id]}"), f"Incorrect source backlink at row {number}")
        url = external_link(source_links, f"B{number}", "/bible/")
        key = (record_id, reference, url)
        require(key not in seen_sources, f"Duplicate supporting source: {key}")
        seen_sources.add(key)
        indexes_by_id[record_id].append(number)
        record["additional_scripture"].append({"reference": reference, "url": url, "context_note": context_note})

    for record in records:
        record_id = record["id"]
        require(display_refs[record_id] == " · ".join(source["reference"] for source in record["additional_scripture"]), f"Supporting references differ for {record_id}")
        if indexes_by_id[record_id]:
            require(cat_links.get(f"X{catalogue_rows[record_id]}") == ("internal", f"'Scripture Sources'!A{indexes_by_id[record_id][0]}"), f"Incorrect supporting source index for {record_id}")
    require(len(cat_links) == 2 * RECORD_COUNT + sum(bool(record["additional_scripture"]) for record in records), "Unexpected Catalogue hyperlinks")
    require(len(source_links) == 2 * SOURCE_COUNT, "Unexpected Scripture Sources hyperlinks")
    return records


def summarize(records: list[dict], books: list[str]) -> dict:
    def counts(key: str) -> dict:
        return dict(sorted(Counter(record[key] for record in records).items()))

    counts_by_book = Counter(record["book"] for record in records)
    linked = sum(record["archived_record_id"] is not None for record in records)
    return {
        "schema_version": 1,
        "workbook": {
            "path": WORKBOOK_PATH, "sha256": WORKBOOK_SHA256,
            "production_url": "https://saints.bible" + LIVE_PATH,
            "staging_url": "https://staging-8e0d-waywardnightjars.wpcomstaging.com" + LIVE_PATH,
        },
        "records": len(records),
        "canonical_books": len(books),
        "audiences": counts("audience"),
        "record_types": counts("record_type"),
        "origins": counts("origin"),
        "books": {book: counts_by_book[book] for book in books},
        "additional_scripture_links": sum(len(record["additional_scripture"]) for record in records),
        "records_with_additional_scripture": sum(bool(record["additional_scripture"]) for record in records),
        "archive_join": {"path": ARCHIVE, "field": "archived_record_id", "matched": linked, "current_only": len(records) - linked},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path, default=ROOT / WORKBOOK_PATH, help="Read another copy of the exact published workbook")
    parser.add_argument("--check", action="store_true", help="Compare generated data with the checked-in files without writing")
    options = parser.parse_args()

    require(hashlib.sha256(options.workbook.read_bytes()).hexdigest() == WORKBOOK_SHA256, "Workbook SHA-256 does not match the verified public snapshot")
    with (ROOT / ARCHIVE).open(encoding="utf-8") as file:
        archive_rows = json.load(file)
    archive_ids = {row["id"] for row in archive_rows}
    require(len(archive_ids) == len(archive_rows) == ARCHIVE_COUNT, "Original archive ID count or uniqueness changed")
    del archive_rows
    books = [item["book"] for item in json.loads((ROOT / "source/translation/book-index.json").read_text(encoding="utf-8"))]
    require(len(books) == len(set(books)) == 70, "Original book register must contain 70 unique books")
    records = extract(options.workbook, archive_ids, books)
    summary = summarize(records, books)
    commands_json = "[\n" + ",\n".join(json.dumps(record, ensure_ascii=False, separators=(",", ":")) for record in records) + "\n]\n"
    outputs = {"commands.json": commands_json, "summary.json": json.dumps(summary, ensure_ascii=False, indent=2) + "\n"}
    output_dir = ROOT / "data/current"
    if options.check:
        for name, content in outputs.items():
            require((output_dir / name).read_bytes() == content.encode("utf-8"), f"Generated output differs from data/current/{name}")
    else:
        output_dir.mkdir(parents=True, exist_ok=True)
        for name, content in outputs.items():
            (output_dir / name).write_bytes(content.encode("utf-8"))
    print(f"Verified {len(records):,} records, {len(books)} books, {SOURCE_COUNT} additional Scripture links, and {len(archive_ids):,} archive joins.")


if __name__ == "__main__":
    main()
