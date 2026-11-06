"""Parse the preserved, rendered Saints.Bible main catalogue with the stdlib.

The input is a read-only WordPress REST snapshot. The parser preserves source
topics, application labels, notes, links and quoted wording; it does not infer
theological classifications or replace a passage quotation with its heading.
Run from any directory: python scripts/parse_main.py
"""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "source/pages/12728-rest.json"
OUTPUT = ROOT / "data/main-records.json"
VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}


@dataclass(eq=False)
class Node:
    tag: str
    attrs: dict[str, str] = field(default_factory=dict)
    children: list["Node | str"] = field(default_factory=list)
    parent: "Node | None" = None

    def nodes(self):
        for child in self.children:
            if isinstance(child, Node):
                yield child
                yield from child.nodes()

    def text(self) -> str:
        def fragments(node):
            for child in node.children:
                if isinstance(child, str):
                    yield child
                elif child.tag == "br":
                    yield " "
                elif child.tag not in {"style", "script"}:
                    yield from fragments(child)
        return re.sub(r"\s+", " ", "".join(fragments(self))).strip()

    def classes(self) -> set[str]:
        return set(self.attrs.get("class", "").split())

    def ancestors(self):
        node = self.parent
        while node is not None:
            yield node
            node = node.parent


class TreeParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("document")
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = Node(tag, dict(attrs), parent=self.stack[-1])
        self.stack[-1].children.append(node)
        if tag not in VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def first(node, predicate):
    return next((child for child in node.nodes() if predicate(child)), None)


def normalized_label(value):
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def source_topic(node):
    """The nearest original topic heading, without interpreting its wording."""
    topic = next((a for a in node.ancestors() if "instructions-topic" in a.classes()), None)
    if topic:
        heading = first(topic, lambda n: n.tag == "h2")
        return heading.text()
    supplement = next(
        (a for a in node.ancestors() if "instructions-supplements" in a.classes()),
        None,
    )
    if supplement:
        # The two supplemental groups have their own explicit source headings.
        last_heading = None
        for child in supplement.children:
            if not isinstance(child, Node):
                continue
            if child.tag == "h3":
                last_heading = child.text()
            if child is node or any(descendant is node for descendant in child.nodes()):
                break
        return re.sub(r"\s*[—–]\s*\d+$", "", last_heading or "Supplementary instructions")
    return None


def paragraphs(node):
    return [n.text() for n in node.nodes() if n.tag == "p" and n.text()]


def classification(node):
    status = next((c[7:] for c in node.classes() if c.startswith("status-")), None)
    if not status:
        return None
    for strong in (n for n in node.nodes() if n.tag == "strong"):
        label = strong.text().rstrip(":")
        if normalized_label(label) == status:
            return label
    raise ValueError(f"No source classification label for {status}")


def citations(node, page_url):
    """Keep a citation for each source role, including repeated source parallels."""
    result = []
    seen = set()
    for p in (n for n in node.nodes() if n.tag == "p"):
        role = "Scripture"

        def visit(element):
            nonlocal role
            for child in element.children:
                if not isinstance(child, Node):
                    continue
                if child.tag == "strong":
                    candidate = child.text()
                    if candidate.endswith(":"):
                        role = candidate[:-1]
                elif child.tag == "a":
                    href = child.attrs.get("href", "")
                    reference = child.text()
                    if "/bible/" in href and re.search(r"\d+:\d+", reference):
                        url = urljoin(page_url, href)
                        key = (reference, url, role)
                        if key not in seen:
                            result.append({"reference": reference, "url": url, "role": role})
                            seen.add(key)
                else:
                    visit(child)
        visit(p)
    return result


def inline_verses(node, page_url):
    """Only extract text explicitly printed after a single verse citation."""
    result = []
    for p in (n for n in node.nodes() if n.tag == "p"):
        anchors = [n for n in p.nodes() if n.tag == "a" and "/bible/" in n.attrs.get("href", "")]
        if len(anchors) != 1:
            continue
        anchor = anchors[0]
        reference = anchor.text()
        if not re.fullmatch(r".+? \d+:\d+", reference):
            continue
        match = re.fullmatch(re.escape(reference) + r"\s+[—–-]\s+(.+)", p.text())
        if match:
            result.append({
                "reference": reference,
                "url": urljoin(page_url, anchor.attrs["href"]),
                "text": match.group(1),
            })
    return result


def crosslinks(node, page_url):
    result = []
    seen = set()
    for anchor in (n for n in node.nodes() if n.tag == "a"):
        href = anchor.attrs.get("href", "")
        if href.startswith("#instruction-") or href.startswith("#study-") or href.startswith("#torah-"):
            url = urljoin(page_url, href)
            key = (anchor.text(), url)
            if key not in seen:
                result.append({"label": anchor.text(), "url": url})
                seen.add(key)
    return result


def make_record(node, record_id, collection, title, anchor, page_url):
    return {
        "id": record_id,
        "collection": collection,
        "category": source_topic(node),
        "classification": classification(node),
        "title": title,
        "source_url": urljoin(page_url, "#" + anchor),
        "source_page_id": 12728,
        "source_anchor": anchor,
        "paragraphs": paragraphs(node),
        "citations": citations(node, page_url),
        "verses": inline_verses(node, page_url),
        "crosslinks": crosslinks(node, page_url),
    }


def parse_main():
    snapshot = json.loads(INPUT.read_text(encoding="utf-8"))
    page_url = snapshot["link"]
    parser = TreeParser()
    parser.feed(snapshot["content"]["rendered"])
    records = []
    for node in parser.root.nodes():
        if "instruction-card" in node.classes():
            heading = first(node, lambda n: n.tag == "h4" and n.attrs.get("id", "").startswith("instruction-"))
            if heading is None:
                raise ValueError("Instruction card lacks stable heading ID")
            anchor = heading.attrs["id"]
            record_id = anchor.removeprefix("instruction-")
            collection = "Torah requirement" if record_id.startswith("C") else "Supplemental instruction"
            title = re.sub(r"^[CMF]\d+\s*·\s*", "", heading.text())
            records.append(make_record(node, record_id, collection, title, anchor, page_url))
        elif node.tag == "details" and re.fullmatch(r"study-\d+", node.attrs.get("id", "")):
            anchor = node.attrs["id"]
            record_id = f"S{int(anchor[6:]):03d}"
            summary = first(node, lambda n: n.tag == "summary")
            title = re.sub(r"^S\d+\s*·\s*", "", summary.text())
            records.append(make_record(node, record_id, "Topical study", title, anchor, page_url))
        elif node.tag == "details" and node.attrs.get("id", "").startswith("torah-"):
            anchor = node.attrs["id"]
            summary = first(node, lambda n: n.tag == "summary")
            records.append(make_record(node, anchor, "Source passage group", summary.text(), anchor, page_url))

    by_id = {r["id"]: r for r in records}
    # The source appends 20 corrective editorial notes outside the study details.
    # Keep them attached to their exact study and retain their own provenance.
    for heading in parser.root.nodes():
        match = re.fullmatch(r"context-study-(\d+)", heading.attrs.get("id", ""))
        if not match:
            continue
        siblings = heading.parent.children
        note_nodes = []
        started = False
        for sibling in siblings:
            if sibling is heading:
                started = True
                continue
            if not started or not isinstance(sibling, Node):
                continue
            if sibling.tag in {"h2", "h3", "h4"}:
                break
            if sibling.tag == "p":
                note_nodes.append(sibling)
        notes = [n.text() for n in note_nodes if n.text()]
        record = by_id[f"S{int(match.group(1)):03d}"]
        record.setdefault("context_notes", []).append({
            "source_url": urljoin(page_url, "#" + heading.attrs["id"]),
            "paragraphs": notes,
        })
        record["paragraphs"].extend(notes)

    expected = {
        "Torah requirement": 1252,
        "Supplemental instruction": 41,
        "Topical study": 157,
        "Source passage group": 216,
    }
    actual = dict(Counter(r["collection"] for r in records))
    if actual != expected or len(by_id) != 1666:
        raise ValueError(f"Catalogue counts differ: {actual}; unique IDs {len(by_id)}")
    if any(not r["category"] or not r["citations"] for r in records):
        raise ValueError("Source topic or Scripture citations missing")
    if {r["id"] for r in records if r["collection"] == "Torah requirement"} != {f"C{i:04d}" for i in range(1, 1253)}:
        raise ValueError("Main requirement ID sequence is incomplete")
    if {r["id"] for r in records if r["collection"] == "Topical study"} != {f"S{i:03d}" for i in range(1, 158)}:
        raise ValueError("Topical study ID sequence is incomplete")
    if any(not r["verses"] for r in records if r["collection"] == "Source passage group"):
        raise ValueError("Passage group has no preserved verse quotations")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return records


if __name__ == "__main__":
    output = parse_main()
    print(json.dumps({
        "records": len(output),
        "collections": dict(Counter(r["collection"] for r in output)),
        "citations": sum(len(r["citations"]) for r in output),
        "quoted_verse_occurrences": sum(len(r["verses"]) for r in output),
        "context_notes": sum(len(r.get("context_notes", [])) for r in output),
    }, ensure_ascii=False))
