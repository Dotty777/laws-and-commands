"""Build the category-sorted repository from archived Saints.Bible sources."""
import collections
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlparse, urlunparse

from parse_main import TreeParser

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://staging-8e0d-waywardnightjars.wpcomstaging.com'
DATE = '2026-11-06'
EXPECTED_COLLECTIONS = {
    'Torah requirement': 1252, 'Supplemental instruction': 41,
    'Source passage group': 216, 'Old Testament passage record': 2509,
    'Topical study': 157, 'Christ study': 105, 'Apostolic teaching': 124,
    'Supplemental passage record': 12, 'Harmony study': 24,
}

def read(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8'))

def write(name, value):
    target = ROOT / name
    target.parent.mkdir(parents=True, exist_ok=True)
    if name == 'data/commands.json':
        # Retain one independently readable record per physical JSON line and
        # avoid repeating indentation throughout the combined catalogue.
        body = '[\n' + ',\n'.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) for r in value) + '\n]\n'
    else:
        body = json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    target.write_text(body, encoding='utf-8')

def slug(value):
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', value).strip('-')

def key_url(value):
    u = urlparse(value)
    return unquote(u.path).rstrip('/') + '#' + unquote(u.fragment).lower()

def natural(value):
    return tuple((0, int(x)) if x.isdigit() else (1, x) for x in re.split(r'(\d+)', str(value)))

def dedupe(items, key):
    result, seen = [], set()
    for item in items:
        k = key(item)
        if k not in seen:
            result.append(item)
            seen.add(k)
    return result

def staging_url(value):
    u = urlparse(value)
    return urlunparse(('https', urlparse(BASE).netloc, u.path, '', '', u.fragment))

def load_translation():
    files = sorted((ROOT / 'source/translation/books').glob('*.json'))
    assert len(files) == 70, f'Expected 70 live book exports, found {len(files)}'
    by_slug, by_url = {}, {}
    for file in files:
        book = json.loads(file.read_text(encoding='utf-8'))
        by_slug[book['slug']] = book
        book['flat_verses'] = []
        for chapter in book['chapters']:
            for verse in chapter['verses']:
                unit = {
                    'reference': f"{book['book']} {verse['chapter']}:{verse['verse']}",
                    'url': staging_url(chapter['url']).split('#')[0] + f"#v{verse['chapter']}-{verse['verse']}",
                    'text': verse['text'], 'chapter': int(verse['chapter']),
                    'verse': str(verse['verse']), 'book': book['slug'],
                    'source_file': file.relative_to(ROOT).as_posix(),
                    'export_generated': book['generated'],
                }
                book['flat_verses'].append(unit)
                by_url[key_url(unit['url'])] = unit
        book['chapter_paths'] = {urlparse(v['url']).path.rstrip('/') for v in book['flat_verses']}
    # Daniel's two separately paged Greek additions are not among the 70 book
    # exports. Their explicit paragraph anchors preserve merged verse units.
    for name, title, book_slug in [
        ('susanna', 'Susanna', 'susanna'),
        ('bel-and-the-dragon', 'Bel and the Dragon', 'bel-and-the-dragon'),
        ('proverbs-24-source-block-2', 'Proverbs', 'proverbs'),
        ('proverbs-31-source-block-2', 'Proverbs', 'proverbs'),
    ]:
        file = ROOT / 'source/translation' / (name + '-page.json')
        if not file.exists():
            continue
        source = json.loads(file.read_text(encoding='utf-8'))
        parser = TreeParser()
        parser.feed(source['content'] if isinstance(source['content'], str) else source['content']['rendered'])
        book = by_slug.setdefault(book_slug, {'slug': book_slug, 'book': title, 'flat_verses': []})
        for node in parser.root.nodes():
            match = re.fullmatch(r'v(\d+)-(\d+[a-z]*)(?:-(\d+[a-z]*))?', node.attrs.get('id', ''), re.I)
            if not match or node.tag != 'p':
                continue
            # The span is an explicit printed verse label, not part of its text.
            label = next((n for n in node.nodes() if n.tag == 'span'), None)
            printed = label.text() if label else ''
            full = node.text()
            text = full[len(printed):].strip() if printed and full.startswith(printed) else full
            chapter, first, last = int(match[1]), match[2], match[3] or match[2]
            verse_label = first if first == last else first + '–' + last
            unit = {
                'reference': f'{title} {chapter}:{verse_label}',
                'url': staging_url(source['link']).split('#')[0] + '#' + node.attrs['id'],
                'text': text, 'chapter': chapter, 'verse': first,
                'verse_end': last, 'book': book_slug,
                'source_file': file.relative_to(ROOT).as_posix(),
                'export_generated': source['modified'],
            }
            book['flat_verses'].append(unit)
            by_url[key_url(unit['url'])] = unit
        book['chapter_paths'] = {urlparse(v['url']).path.rstrip('/') for v in book['flat_verses']}
    return by_slug, by_url

def book_alias(value):
    value = re.sub(r'[^a-z0-9]+', ' ', value.casefold()).strip()
    return {'psalm': 'psalms', 'greek psalm': 'psalms', 'greek psalms': 'psalms',
            'bel and dragon': 'bel and the dragon'}.get(value, value)


def reference_spans(reference, default_book, books):
    """Read every listed span, retaining chapter context across commas/semicolons.

    Numbering in parentheses after a Greek psalm is an alternate numbering,
    not another chapter. Unrecognized residue is reported rather than skipped.
    """
    reference = re.sub(r'(?<=\d)\s*\(\s*\d+\s*\)(?=\s*:)', '', reference)
    reference = re.sub(r'[–—−]', '-', reference.replace('\u00a0', ' '))
    aliases = {book_alias(b['book']): b for b in books.values()}
    aliases.update({book_alias(b['slug']): b for b in books.values()})
    spans, issues = [], []
    chapter, current_book = None, default_book
    parts = re.split(r'\s*[,;]\s*|\s+(?:and|&)\s+(?=\d)', reference.strip(), flags=re.I)
    for part in parts:
        chapter_match = re.search(r'(\d+)\s*:', part)
        body = part.strip()
        if chapter_match:
            prefix = part[:chapter_match.start()].strip()
            if prefix:
                named = aliases.get(book_alias(prefix))
                if named is None:
                    issues.append({'reason': 'unknown_reference_book', 'segment': part, 'book_label': prefix})
                    continue
                current_book = named
            chapter = int(chapter_match[1])
            body = part[chapter_match.end():].strip()
        match = re.fullmatch(r'(\d+[a-z]*)(?:\s*-\s*(?:(\d+)\s*:\s*)?(\d+[a-z]*))?', body, re.I)
        if not match or chapter is None or current_book is None:
            issues.append({'reason': 'unparsed_reference_segment', 'segment': part})
            continue
        first, last = match[1].lower(), (match[3] or match[1]).lower()
        last_chapter = int(match[2] or chapter)
        if last_chapter < chapter or (last_chapter == chapter and natural(last) < natural(first)):
            issues.append({'reason': 'reversed_reference_range', 'segment': part})
            continue
        spans.append((current_book, chapter, first, last_chapter, last))
        chapter = last_chapter
    return spans, issues


def resolve(citation, books, by_url, issues=None):
    """Expand all declared spans and report missing endpoints or partial parsing."""
    local_issues = []
    u = urlparse(citation['url'])
    exact = by_url.get(key_url(citation['url']))
    book = books.get(exact['book']) if exact else None
    if not book:
        # Match the complete published chapter path, including Greek Psalms and
        # separately paged additions. Never mistake Susanna 1 for Daniel 1.
        path = u.path.rstrip('/')
        for candidate in books.values():
            if path in candidate['chapter_paths']:
                book = candidate
                break
    spans, local_issues = reference_spans(citation['reference'], book, books)
    if not book and not spans:
        local_issues.append({'reason': 'missing_book_or_page', 'path': u.path})
    result = []
    for span_book, first_c, first_v, last_c, last_v in spans:
        selected = []
        for unit in span_book['flat_verses']:
            c, v = unit['chapter'], unit['verse']
            end = unit.get('verse_end', v)
            if first_c <= c <= last_c:
                if c == first_c and natural(end) < natural(first_v):
                    continue
                if c == last_c and natural(v) > natural(last_v):
                    continue
                selected.append(unit)
        for endpoint, c, v in [('start', first_c, first_v), ('end', last_c, last_v)]:
            if not any(unit['chapter'] == c and natural(unit['verse']) <= natural(v) <= natural(unit.get('verse_end', unit['verse'])) for unit in selected):
                local_issues.append({'reason': 'missing_range_endpoint', 'endpoint': endpoint,
                                     'requested': f'{span_book["book"]} {c}:{v}'})
        missing_chapters = [c for c in range(first_c, last_c + 1) if not any(v['chapter'] == c for v in selected)]
        if missing_chapters:
            local_issues.append({'reason': 'missing_range_chapter', 'book': span_book['book'], 'chapters': missing_chapters})
        result.extend(selected)
    if issues is not None:
        issues.extend(local_issues)
    return dedupe(result, lambda v: key_url(v['url']))

def markdown_text(value):
    return str(value).replace('\\', '\\\\').replace('*', '\\*').replace('<', '&lt;').replace('>', '&gt;')

def render_record(record):
    lines = [f'<a id="{record["id"]}"></a>', '',
             f'### {record["id"]} · {markdown_text(record["title"])}', '',
             f'**{record["audience"]} · {record["classification"]} · {record["collection"]}**', '',
             record['audience_note'], '', f'[Original research entry]({record["source_url"]})', '']
    if record.get('original_scope'):
        lines += ['**Original scope:** ' + record['original_scope'], '']
    lines += ['**Source wording — Saints Greek-English:**', '']
    for note in record.get('wording_notes', []):
        lines += [markdown_text(note), '']
    for quotation in record['verses']:
        lines += ['> ' + markdown_text(quotation['text']).replace('\n', '\n> '),
                  '>', f'> [{quotation["reference"]}]({quotation["url"]})', '']
    lines += ['<details>', '<summary>All associated verses — Saints Translation</summary>', '',
              'Text from the live staging book exports. The catalogue’s Greek-English source wording is retained separately above.', '']
    for passage in record['associated_passages']:
        lines += [f'**{passage["role"]}: [{passage["reference"]}]({passage["url"]})**', '']
        if passage.get('resolution_issues'):
            lines += ['Reference resolution requires review; see the [resolution audit](../data/unresolved-references.json). Available wording is preserved below.', '']
        if not passage['verses']:
            lines += ['The reference is preserved; no matching verse wording was supplied by this export.', '']
        for verse in passage['verses']:
            lines += [f'> **{verse["reference"]}** — {markdown_text(verse["text"])}', '']
    lines += ['</details>', '']
    notes = record.get('research', {}).get('paragraphs', [])
    if notes:
        lines += ['<details>', '<summary>Full research notes and original quoted wording</summary>', '']
        lines += [markdown_text(p) + '\n' for p in notes]
        for quotation in record.get('research', {}).get('verses', []):
            if quotation.get('text'):
                lines += ['> ' + markdown_text(quotation['text']).replace('\n', '\n> '),
                          '>', f'> [{quotation["reference"]}]({quotation["url"]})', '']
        lines += ['</details>', '']
    return '\n'.join(lines)


def render_category(name, items):
    """Keep every category browsable through small, linked Markdown files."""
    relative = 'categories/' + slug(name) + '.md'
    header = ['# ' + name, '', '[Category index](../README.md) · [Import methodology](../IMPORT.md)', '',
              f'{len(items):,} study records, imported from Saints.Bible staging on 6 November 2026.', '',
              'General and Personal describe the stated audience. Classifications and scope notes reproduce the source catalogue. Records overlap; these are not unique command counts.', '']
    rendered = {r['id']: render_record(r) for r in items}

    def body(group):
        lines, current = [], None
        for record in group:
            label = (record['audience'], record['classification'])
            if label != current:
                lines += ['## ' + ' · '.join(label), '']
                current = label
            lines += [rendered[record['id']]]
        return '\n'.join(lines)

    full = '\n'.join(header) + body(items)
    limit = 220_000
    if len(full.encode('utf-8')) <= limit:
        (ROOT / relative).parent.mkdir(parents=True, exist_ok=True)
        (ROOT / relative).write_text(full.rstrip() + '\n', encoding='utf-8')
        for record in items:
            record['record_file'] = relative
        return relative, [relative]

    groups, group, size = [], [], 0
    for record in items:
        record_size = len(rendered[record['id']].encode('utf-8')) + 200
        if group and size + record_size > limit - 1800:
            groups.append(group)
            group, size = [], 0
        group.append(record)
        size += record_size
    if group:
        groups.append(group)
    parts = [f'categories/{slug(name)}/part-{i:03}.md' for i in range(1, len(groups) + 1)]
    index = header + ['The records are divided into linked parts, preserving audience and classification order.', '',
                      '| Part | Records | First record | Last record |', '| --- | ---: | --- | --- |']
    for i, (group, part) in enumerate(zip(groups, parts), 1):
        short = Path(part).name
        relative_part = f'{slug(name)}/{short}'
        index.append(f'| [Part {i}]({relative_part}) | {len(group):,} | [{group[0]["id"]}]({relative_part}#{group[0]["id"]}) | [{group[-1]["id"]}]({relative_part}#{group[-1]["id"]}) |')
        navigation = [f'[Category overview](../{slug(name)}.md)', '[All categories](../../README.md)']
        if i > 1:
            navigation.append(f'[Previous part]({Path(parts[i - 2]).name})')
        if i < len(parts):
            navigation.append(f'[Next part]({Path(parts[i]).name})')
        text = f'# {name} — Part {i}\n\n' + ' · '.join(navigation) + '\n\n' + body(group)
        target = ROOT / part
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text.rstrip() + '\n', encoding='utf-8')
        for record in group:
            record['record_file'] = part
    (ROOT / relative).write_text('\n'.join(index).rstrip() + '\n', encoding='utf-8')
    return relative, parts

def main():
    records = read('data/audience-records.json')
    assert len(records) == 4440 and len({r['id'] for r in records}) == 4440
    assert collections.Counter(r['collection'] for r in records) == EXPECTED_COLLECTIONS
    support = read('data/main-records.json') + read('data/supporting-records.json')
    research_by_url = {key_url(r['source_url']): r for r in support}
    research_by_id = {r['id']: r for r in support}
    books, by_url = load_translation()
    verse_bank, unresolved, missing_research = {}, [], []
    for record in records:
        research = research_by_url.get(key_url(record['source_url'])) or research_by_id.get(record['id'])
        if research:
            record['research'] = research
        else:
            missing_research.append({'id': record['id'], 'source_url': record['source_url']})
        # Explicit printed quotations are independent evidence of an associated
        # reference even when a source parser stored them only under verses.
        quoted_cites = [
            {'reference': q['reference'], 'url': q['url'], 'role': 'Original quoted wording'}
            for q in list(record.get('verses', [])) + (research.get('verses', []) if research else [])
            if q.get('reference') and q.get('url')
        ]
        cites = list(record['citations']) + (research.get('citations', []) if research else []) + quoted_cites
        record['citations'] = dedupe(cites, lambda c: (c['reference'], key_url(c['url']), c.get('role', 'Related Scripture')))
        record['associated_passages'] = []
        for cite in record['citations']:
            resolution_issues = []
            units = resolve(cite, books, by_url, resolution_issues)
            keys = []
            for unit in units:
                k = key_url(unit['url'])
                verse_bank[k] = unit
                keys.append(k)
            passage = {**cite, 'role': cite.get('role', 'Related Scripture'), 'verse_keys': keys,
                       'verses': [{'reference': v['reference'], 'url': v['url'], 'text': v['text']} for v in units]}
            if resolution_issues:
                passage['resolution_issues'] = resolution_issues
            record['associated_passages'].append(passage)
            if resolution_issues or not units:
                unresolved.append({'id': record['id'], **cite, 'resolved_verse_units': len(units),
                                   'issues': resolution_issues or [{'reason': 'no_matching_verse_units'}]})
        record['category_file'] = 'categories/' + slug(record['category']) + '.md'
    categories = collections.defaultdict(list)
    for record in records:
        categories[record['category']].append(record)
    assert len(categories) == 50, f'Expected 50 categories, found {len(categories)}'
    counts = []
    for name in sorted(categories, key=str.casefold):
        items = categories[name]
        items.sort(key=lambda r: (r['audience'] != 'General', r['classification'].casefold(), natural(r['id'])))
        relative, parts = render_category(name, items)
        audience = collections.Counter(r['audience'] for r in items)
        counts.append({'category': name, 'file': relative, 'parts': parts, 'records': len(items), 'General': audience['General'], 'Personal': audience['Personal']})
    records.sort(key=lambda r: (r['category'].casefold(), r['audience'] != 'General', r['classification'].casefold(), natural(r['id'])))
    write('data/commands.json', records)
    write('data/verses.json', dict(sorted(verse_bank.items())))
    write('data/categories.json', counts)
    write('data/unresolved-references.json', unresolved)
    write('data/missing-research.json', missing_research)
    wording_reviews = [
        {'id': r['id'], 'source_url': r['source_url'], 'audience_archive': r['source_archive'],
         'notes': [n for n in r.get('wording_notes', []) if 'source review needed' in n.casefold()]}
        for r in records if any('source review needed' in n.casefold() for n in r.get('wording_notes', []))
    ]
    write('data/source-wording-review.json', wording_reviews)
    write('data/summary.json', {
        'source': BASE, 'imported_date': DATE, 'records': len(records), 'categories': len(categories),
        'audiences': dict(collections.Counter(r['audience'] for r in records)),
        'classifications': dict(sorted(collections.Counter(r['classification'] for r in records).items())),
        'collections': dict(sorted(collections.Counter(r['collection'] for r in records).items())),
        'associated_unique_verse_units': len(verse_bank), 'unresolved_reference_occurrences': len(unresolved),
        'records_with_full_research': sum('research' in r for r in records),
        'source_wording_review_records': len(wording_reviews),
    })
    manifest = []
    for file in sorted((ROOT / 'source').rglob('*')):
        if file.is_file():
            body = file.read_bytes()
            manifest.append({'file': file.relative_to(ROOT).as_posix(), 'bytes': len(body), 'sha256': hashlib.sha256(body).hexdigest()})
    write('source/manifest.json', [m for m in manifest if m['file'] != 'source/manifest.json'])
    summary = read('data/summary.json')
    lines = ['# Laws and commands', '',
             '## Current Saints.Bible catalogue', '',
             '[Browse the current catalogue](browse/README.md) · [By Bible book](browse/books/README.md) · [By record type](browse/record-types/README.md) · [By topic](browse/categories/README.md)', '',
             'The current catalogue contains **4,999 study records** across all 70 books, including **559 added since the 6 November 2026 import**. It has **4,301 General** and **698 Personal** records and **269 supplementary Scripture links**.', '',
             'The seven record types are Law, Command, Commission, Instruction, Wisdom, Study Context, and Mixed. Record type describes the form of the material. Origin, original audience, and application are recorded separately.', '',
             '[Download the current workbook](source/current/Saints-Bible-Instructions-Catalogue-Complete-Record-Types.xlsx) · [Current catalogue JSON](data/current/commands.json) · [Current summary](data/current/summary.json) · [Live catalogue](https://saints.bible/instructions/)', '',
             '## Archival import and category index', '',
             'The **6 November 2026** import preserves **4,440 study records** from [Saints.Bible staging](' + BASE + '/instructions/) in **50 topical categories**, with the source wording, associated verses, classifications, audience notes, and original research.', '',
             '**3,869 General · 571 Personal.** The archive contains overlapping commandments, historical directions, passage groups, and teaching studies. Its totals count study records.', '',
             '[Methodology and coverage](IMPORT.md) · [Archival catalogue JSON](data/commands.json) · [Archival verse index](data/verses.json) · [Archival summary](data/summary.json)', '',
             'Saints Translation and the catalogue’s Saints Greek-English wording are kept distinct. Source scope, disputed classifications, historical settings, and audience review notes remain attached to each record. Three [source wording review notices](data/source-wording-review.json) are preserved.', '',
             '| Category | General | Personal | Total |', '| --- | ---: | ---: | ---: |']
    for c in counts:
        lines.append(f'| [{c["category"]}]({c["file"]}) | {c["General"]:,} | {c["Personal"]:,} | {c["records"]:,} |')
    lines += ['', 'Texts are attributed to Saints.Bible. The Saints Translation exports declare [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); preserve their attribution and source numbering when reusing them.', '']
    (ROOT / 'README.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=True, indent=2))

if __name__ == '__main__':
    main()
