"""Extract original supporting research and explicit Scripture quotations.

Run with Python 3.12+ and lxml. Reads only the archived source/pages JSON files.
No editorial command summary is promoted to a Scripture quotation. Quoted ranges
remain ranges; the importer does not invent boundaries for individual verses.
"""

from __future__ import annotations

import copy
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urljoin

from lxml import html


ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "source" / "pages"
OUT = ROOT / "data"
BASE = "https://staging-8e0d-waywardnightjars.wpcomstaging.com/"
SPACE = re.compile(r"\s+")
VERSE_URL = re.compile(r"/bible/[^#]+#v\d+-\d+(?:$|[&-])")
REFERENCE = re.compile(r"\b\d+(?:\s*\(\d+\))?:\d+")
REPORT = {"unlinked_blockquotes": [], "multi_citation_blockquotes": [],
          "empty_records": [], "missing_pages": [], "warnings": []}


def text(node):
    if node is None:
        return ""
    parts = []

    def collect(element):
        if element.text:
            parts.append(element.text)
        for child in element:
            if isinstance(child.tag, str):
                if child.tag == "br":
                    parts.append(" ")
                collect(child)
            if child.tail:
                parts.append(child.tail)

    collect(node)
    return SPACE.sub(" ", "".join(parts)).strip()


def load_pages():
    pages = {}
    # A REST snapshot has rendered shortcode content and wins over a raw page.
    for file in sorted(PAGES.glob("*.json"), key=lambda p: ("-rest" in p.stem, p.name)):
        p = json.loads(file.read_text(encoding="utf-8"))
        if "data" in p and "id" not in p:
            p = p["data"]
        if "id" not in p:
            continue
        content = p.get("content", "")
        if isinstance(content, dict):
            content = content.get("rendered", content.get("raw", ""))
        if not content:
            continue
        p["content_html"] = content
        p["document"] = html.fromstring(content)
        p["link"] = p.get("link", BASE)
        pages[p["id"]] = p
    return pages


def is_verse_link(a):
    url = a.get("href", "")
    # Several Saints poetry pages and Proverbs source blocks do not have a
    # chapter-N URL or verse fragment; their explicit range label identifies
    # the citation without inventing a new target URL.
    return bool(VERSE_URL.search(url) or (
        "/bible/" in url and REFERENCE.search(text(a)) and
        re.search(r"/(?:chapter-|greek-psalm-)", url)))


def citations(node, page):
    found = []
    seen = set()
    for a in node.xpath(".//a[@href]"):
        if not is_verse_link(a):
            continue
        url = urljoin(page["link"], a.get("href"))
        reference = text(a)
        parent_p = next((x for x in a.iterancestors() if x.tag == "p"), None)
        labels = parent_p.xpath(".//strong") if parent_p is not None else []
        label = "; ".join(text(x).rstrip(":") for x in labels)
        role = "associated"
        if any(x.tag == "cite" for x in a.iterancestors()):
            role = "quotation"
        elif re.search(r"\b(?:Original Scripture|Scripture|Torah|Saints Translation.*Law)\b", label, re.I):
            role = "original"
        elif label:
            role = label
        key = (reference, url, role)
        if key not in seen:
            entry = {"reference": reference, "url": url, "role": role}
            if label:
                entry["source_label"] = label
            found.append(entry)
            seen.add(key)
    return found


def quotation_units(node, page, source_url=None):
    """Extract two explicit source patterns, leaving range boundaries intact."""
    found = []
    source_url = source_url or page["link"]
    for p in node.xpath(".//p[a[@href]]"):
        if any(x.tag == "blockquote" for x in p.iterancestors()):
            continue
        a = next((a for a in p.xpath("./a[@href]") if is_verse_link(a)), None)
        if a is None:
            continue
        reference = text(a)
        match = re.match(r"^" + re.escape(reference) + r"\s*[—–]\s*(.+)$", text(p))
        if not match:
            continue
        found.append({"reference": reference,
                      "url": urljoin(page["link"], a.get("href")),
                      "text": match.group(1), "extraction": "linked-verse-paragraph",
                      "source_url": source_url, "page_id": page["id"]})
    quotes = node.xpath(".//blockquote[not(ancestor::blockquote)]")
    if node.tag == "blockquote":
        quotes.insert(0, node)
    for quote in quotes:
        cites = [a for a in quote.xpath(".//cite//a[@href]") if is_verse_link(a)]
        # Citation text is metadata, not part of the quotation wording.
        clean = copy.deepcopy(quote)
        for cite in clean.xpath(".//cite"):
            cite.drop_tree()
        paragraphs = clean.xpath(".//p")
        body = "\n\n".join(text(p) for p in paragraphs if text(p)) if paragraphs else text(clean)
        if not body:
            continue
        refs = [{"reference": text(a), "url": urljoin(page["link"], a.get("href"))}
                for a in cites]
        if not refs:
            REPORT["unlinked_blockquotes"].append({"page_id": page["id"],
                                                   "source_url": source_url, "text": body})
            continue
        if len(refs) > 1:
            REPORT["multi_citation_blockquotes"].append({"page_id": page["id"],
                    "source_url": source_url, "references": refs})
        # Multiple citations describe one source quote. Retain the complete
        # citation list without pretending to segment its text into verses.
        found.append({"reference": "; ".join(r["reference"] for r in refs),
                      "url": refs[0]["url"], "text": body,
                      "references": refs, "extraction": "blockquote-with-citation",
                      "source_url": source_url, "page_id": page["id"]})
    unique = {}
    for q in found:
        unique.setdefault((q["reference"], q["url"], q["text"]), q)
    return list(unique.values())


def preceding(node, tag):
    values = node.xpath(f"preceding::{tag}[1]")
    return text(values[0]) if values else ""


def make_record(record_id, title, collection, category, page, node, anchor, classification=None):
    source_url = page["link"].split("#")[0] + "#" + anchor
    paragraphs = [text(p) for p in node.xpath(".//p") if text(p)]
    record = {"id": record_id, "title": title, "collection": collection,
              "category": category, "source_url": source_url, "page_id": page["id"],
              "paragraphs": paragraphs, "citations": citations(node, page),
              "verses": quotation_units(node, page, source_url)}
    if classification:
        record["classification"] = classification
    if not paragraphs:
        REPORT["empty_records"].append(record_id)
    return record


def parse_supporting(pages):
    records = []
    for page_id in range(43942, 43985):
        page = pages.get(page_id)
        if page is None:
            REPORT["missing_pages"].append(page_id)
            continue
        for node in page["document"].xpath(".//details[starts-with(@id, 'ot-')]"):
            anchor = node.get("id")
            classification = re.sub(r"\s*·\s*\d+ passage records?$", "", preceding(node, "h3"))
            records.append(make_record(anchor, text(node.find("summary")),
                        "Expanded Old Testament passage records", preceding(node, "h2"),
                        page, node, anchor, classification))
    for page_id in [12702, 12703, 12704, 12705, 12706, 12707, 12723]:
        page = pages.get(page_id)
        if page is None:
            REPORT["missing_pages"].append(page_id)
            continue
        apostolic = page_id == 12723
        prefix = "a" if apostolic else "k"
        for heading in page["document"].xpath(f".//*[@id[starts-with(., '{prefix}')]]"):
            anchor = heading.get("id", "")
            match = re.fullmatch(prefix + r"(\d+)", anchor)
            if not match:
                continue
            ancestors = heading.xpath("ancestor::div[contains(concat(' ', normalize-space(@class), ' '), ' saints-command-card ')][1]")
            if not ancestors:
                raise ValueError(f"No study card for {page_id}#{anchor}")
            record_id = ("A" if apostolic else "K") + match.group(1).zfill(3)
            title = re.sub(r"^\d+\.\s*", "", text(heading))
            category = preceding(heading, "h3" if apostolic else "h2")
            records.append(make_record(record_id, title,
                        "Apostolic teachings" if apostolic else "Christ studies",
                        category, page, ancestors[0], anchor))
    for page_id in range(12730, 12736):
        page = pages.get(page_id)
        if page is None:
            REPORT["missing_pages"].append(page_id)
            continue
        for heading in page["document"].xpath(".//h2[starts-with(@id, 'w')]"):
            anchor = heading.get("id")
            if not re.fullmatch(r"w\d+-\d+", anchor):
                continue
            section = html.Element("div")
            section.append(copy.deepcopy(heading))
            sibling = heading.getnext()
            while sibling is not None and sibling.tag != "h2":
                section.append(copy.deepcopy(sibling))
                sibling = sibling.getnext()
            records.append(make_record(anchor, text(heading), "Harmony studies",
                                       text(heading), page, section, anchor))
    page = pages.get(43891)
    if page is None:
        REPORT["missing_pages"].append(43891)
    else:
        for heading in page["document"].xpath(".//h3[starts-with(@id, 'X')]"):
            anchor = heading.get("id")
            if not re.fullmatch(r"X\d{3}", anchor):
                continue
            section = html.Element("div")
            sibling = heading.getnext()
            while sibling is not None and sibling.tag not in {"h2", "h3"}:
                section.append(copy.deepcopy(sibling))
                sibling = sibling.getnext()
            classification = None
            for paragraph in section.xpath(".//p"):
                match = re.search(r"Record type:\s*(.+)$", text(paragraph))
                if match:
                    classification = match.group(1).rstrip(".")
                    break
            records.append(make_record(anchor, re.sub(r"^X\d+\s*·\s*", "", text(heading)),
                        "Supplemental passages", "Selected additional instruction records",
                        page, section, anchor, classification))
    return records


def build_quote_pool(pages):
    pool = {}
    for page in pages.values():
        for q in quotation_units(page["document"], page):
            key = (q["reference"], q["url"], q["text"])
            origin = {"page_id": q["page_id"], "source_url": q["source_url"]}
            if key not in pool:
                pool[key] = {**q, "sources": [origin]}
            elif origin not in pool[key]["sources"]:
                pool[key]["sources"].append(origin)
    variants = defaultdict(set)
    for q in pool.values():
        variants[q["url"]].add(q["text"])
    REPORT["quotation_urls_with_text_variants"] = [
        {"url": url, "text_variants": len(texts)}
        for url, texts in sorted(variants.items()) if len(texts) > 1]
    return sorted(pool.values(), key=lambda q: (q["url"], q["reference"], q["text"]))


def main():
    pages = load_pages()
    records = parse_supporting(pages)
    ids = [r["id"] for r in records]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate supporting record IDs")
    counts = Counter(r["collection"] for r in records)
    expected = {"Expanded Old Testament passage records": 2509, "Christ studies": 105,
                "Apostolic teachings": 124, "Harmony studies": 24, "Supplemental passages": 12}
    if dict(counts) != expected:
        raise ValueError(f"Supporting record counts differ: {dict(counts)}")
    quotes = build_quote_pool(pages)
    REPORT["record_counts"] = dict(counts)
    REPORT["supporting_records"] = len(records)
    REPORT["quotation_variants"] = len(quotes)
    REPORT["source_pages_scanned"] = len(pages)
    OUT.mkdir(exist_ok=True)
    for name, data in [("supporting-records.json", records), ("quoted-verses.json", quotes),
                       ("supporting-parse-report.json", REPORT)]:
        (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "counts": dict(counts), "quotes": len(quotes),
                      "unlinked_quotes": len(REPORT["unlinked_blockquotes"]),
                      "multi_citation_quotes": len(REPORT["multi_citation_blockquotes"])}))


if __name__ == "__main__":
    main()
