"""Validate and normalize the Torah Law category layer, and write its CSV copy.

The layer adds two editorial study labels to every Torah Law record: form (the Jewish division
into positive and negative commandments) and category (the traditional Christian division into
moral, ceremonial and civil law). The site's classification field is separate and unchanged.
"""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import io
import json
import re
from pathlib import Path

from build_catalogue import load_translation, resolve

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = "data/current/commands.json"
LAYER = "data/current/torah-law-categories.json"
LAYER_CSV = "data/current/torah-law-categories.csv"
FORMS = ("Positive", "Negative", "Permission")
CATEGORIES = ("Moral", "Ceremonial", "Civil")
AREAS = ("Sacrifice and offerings", "Priesthood and sanctuary", "Dietary laws", "Ritual purity",
         "Festivals and holy days", "Signs, vows and dedications")
CONFIDENCE = ("high", "medium", "low")
RECORD_KEYS = ("id", "reference", "title", "form", "form_mixed", "form_basis", "category", "second_category",
               "ceremonial_area", "confidence", "review_reasons", "note", "adjudicated", "maimonides_613")
CSV_COLUMNS = (("Record ID", "id"), ("Scripture", "reference"), ("Study record", "title"), ("Form", "form"),
               ("Form mixed", "form_mixed"), ("Form basis", "form_basis"), ("Category", "category"),
               ("Second category", "second_category"), ("Ceremonial area", "ceremonial_area"),
               ("Confidence", "confidence"), ("Review reasons", "review_reasons"), ("Note", "note"),
               ("Adjudication", "adjudicated"), ("Maimonides 613", "maimonides_613"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def verify_form_basis(record: dict, source_verses: dict[str, str]) -> None:
    basis = re.fullmatch(r'[^"]*"([^"]+)" \((\d+:\d+[a-z]?)\)', record["form_basis"])
    rid = record["id"]
    require(basis is not None, f"Missing form-basis quotation or verse for {rid}")
    excerpt, reference = basis.groups()
    require(reference in source_verses, f"Form basis cites a verse outside the record for {rid}: {reference}")

    def words(text: str) -> str:
        return " ".join(re.findall(r"[^\W_]+(?:'[^\W_]+)*", text.casefold().replace("’", "'")))

    remaining = f" {words(source_verses[reference])} "
    for fragment in re.split(r"…|\.{3}", excerpt):
        needle = f" {words(fragment)} "
        position = remaining.find(needle)
        require(position >= 0, f"Form-basis quotation differs from Saints Translation for {rid}: {reference}")
        remaining = remaining[position + len(needle) - 1:]


def counts(records: list[dict]) -> dict:
    def tally(key: str, order: tuple) -> dict:
        found = Counter(r[key] for r in records)
        return {name: found[name] for name in order}
    return {
        "torah_laws": len(records),
        "form": tally("form", FORMS),
        "form_mixed": sum(r["form_mixed"] for r in records),
        "category": tally("category", CATEGORIES),
        "ceremonial_area": {area: sum(r["category"] == "Ceremonial" and r["ceremonial_area"] == area for r in records) for area in AREAS},
        "second_category": {name: sum(r["second_category"] == name for r in records) for name in CATEGORIES},
        "form_by_category": {cat: {form: sum(r["category"] == cat and r["form"] == form for r in records) for form in FORMS}
                             for cat in CATEGORIES},
        "flagged_for_review": sum(bool(r["review_reasons"]) for r in records),
    }


def build() -> dict[str, str]:
    catalogue = json.loads((ROOT / CATALOGUE).read_text(encoding="utf-8"))
    layer = json.loads((ROOT / LAYER).read_text(encoding="utf-8"))
    torah = [r for r in catalogue if r["study_placement"] == "Torah Law"]
    by_id = {r["id"]: r for r in torah}
    records = layer["records"]
    ids = [r["id"] for r in records]
    require(len(ids) == len(set(ids)), "Duplicate record in the category layer")
    require(set(ids) == set(by_id), "The category layer must cover exactly the Torah Law records")
    order = {r["id"]: n for n, r in enumerate(torah)}
    records.sort(key=lambda r: order[r["id"]])
    books, verses_by_url = load_translation()
    for r in records:
        rid = r["id"]
        require(tuple(r) == RECORD_KEYS, f"Unexpected keys for {rid}")
        require(r["reference"] == by_id[rid]["reference"] and r["title"] == by_id[rid]["title"], f"Reference or title differs from the catalogue for {rid}")
        require(r["form"] in FORMS and isinstance(r["form_mixed"], bool) and r["form_basis"].strip(), f"Invalid form for {rid}")
        verses = resolve({"reference": r["reference"], "url": by_id[rid]["scripture_url"]}, books, verses_by_url)
        verify_form_basis(r, {f"{v['chapter']}:{v['verse']}": v["text"] for v in verses})
        require(r["category"] in CATEGORIES and r["second_category"] in ("",) + CATEGORIES and r["second_category"] != r["category"], f"Invalid category for {rid}")
        ceremonial = "Ceremonial" in (r["category"], r["second_category"])
        require((r["ceremonial_area"] in AREAS) if ceremonial else r["ceremonial_area"] == "", f"Invalid ceremonial area for {rid}")
        require(r["confidence"] in CONFIDENCE and isinstance(r["review_reasons"], list) and isinstance(r["maimonides_613"], list), f"Invalid review fields for {rid}")
    layer["torah_laws"] = len(records)
    layer["counts"] = counts(records)
    ordered = {key: layer[key] for key in ("schema_version", "description", "catalogue", "torah_laws", "counts", "definitions", "records")}
    lines = ["{"]
    head = list(ordered.items())
    for n, (key, value) in enumerate(head):
        if key == "records":
            lines.append(f'  "records": [')
            lines.append(",\n".join("    " + json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in records))
            lines.append("  ]")
        else:
            text = json.dumps(value, ensure_ascii=False, indent=2).replace("\n", "\n  ")
            lines.append(f'  "{key}": {text}' + ("," if n < len(head) - 1 else ""))
    json_text = "\n".join(lines) + "\n}\n"
    json.loads(json_text)

    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow([header for header, _ in CSV_COLUMNS])
    for r in records:
        row = []
        for _, key in CSV_COLUMNS:
            value = r[key]
            if isinstance(value, bool):
                value = "yes" if value else ""
            elif isinstance(value, list):
                value = "; ".join(value)
            row.append(value)
        writer.writerow(row)
    return {LAYER: json_text, LAYER_CSV: buffer.getvalue()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify the layer and its CSV without writing")
    options = parser.parse_args()
    outputs = build()
    if options.check:
        for name, content in outputs.items():
            require((ROOT / name).exists() and (ROOT / name).read_bytes() == content.encode("utf-8"), f"{name} is not normalized. Run scripts/build_torah_law_categories.py.")
    else:
        for name, content in outputs.items():
            (ROOT / name).write_bytes(content.encode("utf-8"))
    layer = json.loads(outputs[LAYER])
    c = layer["counts"]
    print(f"{'Verified' if options.check else 'Built'} categories for {c['torah_laws']:,} Torah Law records: "
          + ", ".join(f"{v} {k}" for k, v in c["form"].items()) + "; "
          + ", ".join(f"{v} {k}" for k, v in c["category"].items()) + f"; {c['flagged_for_review']} flagged for review.")


if __name__ == "__main__":
    main()
