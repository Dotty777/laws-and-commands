"""Convert archived rendered audience cards into a lossless, linked record index."""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urljoin

from lxml import html

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://staging-8e0d-waywardnightjars.wpcomstaging.com"


def text(node) -> str:
    return re.sub(r"\s+", " ", node.text_content()).strip()


def classes(name: str) -> str:
    return "contains(concat(' ', normalize-space(@class), ' '), ' " + name + " ')"


def parse_page(payload: dict, audience: str, archive: str) -> list[dict]:
    tree = html.fromstring(payload["content"]["rendered"])
    records = []
    for card in tree.xpath(f".//details[{classes('saints-audience-entry')}]"):
        record_id = card.get("id").removeprefix("audience-")
        summary = text(card.xpath("./summary")[0])
        title = summary.split(" · ", 1)[-1]
        paragraphs = [text(p) for p in card.xpath("./p")]
        field_values = {}
        for paragraph in paragraphs:
            if ":" in paragraph:
                label, value = paragraph.split(":", 1)
                field_values[label] = value.strip()
        classification_and_collection = field_values.get("Classification", "")
        classification, separator, collection = classification_and_collection.rpartition(" · ")
        if not separator:
            raise ValueError(f"Classification/collection missing for {record_id}")
        source_links = card.xpath("./p/a[contains(normalize-space(.), 'Full research entry')]/@href")
        if len(source_links) != 1:
            raise ValueError(f"Full research source link missing for {record_id}")
        source_category = field_values.get("Topic", "")
        category = source_category or "Cross-Scripture studies"
        category_note = ""
        if not source_category:
            category_note = (
                "The audience card omits a Topic paragraph. The main Instructions overview's "
                "instruction-topic-counts table places these 36 records under Cross-Scripture "
                "studies (34 General and 2 Personal)."
            )
        citations = []
        for item in card.xpath("./ul/li"):
            role = text(item).split(":", 1)[0].strip()
            for anchor in item.xpath(".//a[@href]"):
                citations.append({"reference": text(anchor), "url": urljoin(SITE, anchor.get("href")), "role": role})
        verses = []
        wording_notes = []
        for wording in card.xpath(f"./div[{classes('saints-greek-wording')}]"):
            wording_notes.extend(text(p) for p in wording.xpath("./p"))
            for quote in wording.xpath("./blockquote"):
                citation = quote.xpath("./cite/a[@href]")
                if len(citation) != 1:
                    raise ValueError(f"Quote citation missing for {record_id}")
                chunks = []
                units = []
                for p in quote.xpath("./p"):
                    # A small element is a printed verse label, not part of the quotation.
                    labels = [text(small) for small in p.xpath(".//small")]
                    for small in p.xpath(".//small"):
                        small.drop_tree()
                    chunks.append(text(p))
                    units.append({"label": " ".join(labels), "text": text(p)})
                verses.append({"reference": text(citation[0]), "url": urljoin(SITE, citation[0].get("href")), "text": "\n".join(chunks), "verse_units": units})
        records.append({
            "id": record_id,
            "title": title,
            "collection": collection,
            "category": category,
            "source_category": source_category,
            "category_note": category_note,
            "classification": classification,
            "audience": audience.title(),
            "audience_note": field_values.get("Audience", ""),
            "original_scope": field_values.get("Original scope", ""),
            "source_url": urljoin(SITE, source_links[0]),
            "source_page_id": payload["id"],
            "source_archive": archive,
            "paragraphs": paragraphs,
            "wording_notes": wording_notes,
            "citations": citations,
            "verses": verses,
        })
    return records


def main() -> None:
    records = []
    for archive in sorted((ROOT / "source" / "audience").glob("*.json")):
        audience = archive.stem.split("-", 1)[0]
        payload = json.loads(archive.read_text(encoding="utf-8-sig"))
        records.extend(parse_page(payload, audience, archive.relative_to(ROOT).as_posix()))
    counts = Counter(record["audience"] for record in records)
    assert counts == {"General": 3869, "Personal": 571}, counts
    assert len({record["id"] for record in records}) == len(records) == 4440
    assert len({record["category"] for record in records}) == 50
    fallback = [record for record in records if not record["source_category"]]
    assert Counter(record["audience"] for record in fallback) == {"General": 34, "Personal": 2}
    assert Counter(record["collection"] for record in fallback) == {"Supplemental passage record": 12, "Harmony study": 24}
    assert all(record["title"] and record["category"] and record["citations"] for record in records)
    collections = Counter(record["collection"] for record in records)
    expected_collections = {
        "Torah requirement": 1252,
        "Supplemental instruction": 41,
        "Source passage group": 216,
        "Old Testament passage record": 2509,
        "Topical study": 157,
        "Christ study": 105,
        "Apostolic teaching": 124,
        "Supplemental passage record": 12,
        "Harmony study": 24,
    }
    assert collections == expected_collections, collections
    out = ROOT / "data" / "audience-records.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "audience": counts, "categories": len({r['category'] for r in records}), "collections": collections, "verses": sum(len(r["verses"]) for r in records), "without_inline_wording": [r["id"] for r in records if not r["verses"]]}, indent=2))


if __name__ == "__main__":
    main()
