"""Shared helpers for the Laws, Commands and Instructions completeness audit.

Loads the 70 Saints Translation book exports (plus the supplementary blocks the
exports omit: Susanna, Bel and the Dragon, Proverbs 24:23-34, 30:15-33,
31:10-31), parses catalogue Scripture references, and maps every record to
the verses it covers.
"""
import json, re, glob, os, collections

REPO = "/home/claude/repos/laws-and-commands/"
WORK = "/home/claude/work/"

# pseudo-book names used in references -> (book, chapter offset or fixed chapter)
ALIASES = {
    "Greek Psalm": ("Psalms", None), "Greek Psalms": ("Psalms", None),
    "Psalm": ("Psalms", None), "Song of Solomon": ("Song of Songs", None),
    "Susanna": ("Daniel", 13), "Bel and the Dragon": ("Daniel", 14), "Bel and Dragon": ("Daniel", 14),
}
FIXED_CH_NAMES = {("Daniel", 13): "Susanna", ("Daniel", 14): "Bel and the Dragon"}


def book_order():
    s = json.load(open(REPO + "data/current/summary.json"))
    return list(s["books"].keys())


def parse_label(label):
    """'35a' -> (35, 35, 'a'); '7-8' -> (7, 8, ''); 'preface' -> (0, 0, 'preface')."""
    label = str(label).replace("–", "-")
    m = re.fullmatch(r"(\d+)([a-z]*)(?:-(\d+)([a-z]*))?", label)
    if not m:
        return (0, 0, label)
    n0 = int(m.group(1))
    n1 = int(m.group(3)) if m.group(3) else n0
    return (n0, n1, m.group(2))


class Bible:
    def __init__(self, include_extra=True):
        self.order = book_order()
        self.verses = []
        self.by_book = collections.defaultdict(list)
        self.by_chapter = collections.OrderedDict()
        self.key = {}
        files = {}
        for f in glob.glob(REPO + "source/translation/books/*.json"):
            b = json.load(open(f))
            files[b["book"]] = b
        extra = {}
        if include_extra and os.path.exists(WORK + "extra_blocks.json"):
            extra = json.load(open(WORK + "extra_blocks.json"))
        self.chapter_url = {}
        for book in self.order:
            b = files[book]
            div = b["url"].split("/bible/")[1].split("/")[0]
            chapters = [(c["chapter"], c["verses"], "export", c.get("url", "")) for c in b["chapters"]]
            for blk in extra.get(book, []):
                chapters.append((blk["chapter"], blk["verses"], blk["block"], blk.get("url", "")))
            chapters.sort(key=lambda t: (t[0], 0 if t[2] == "export" else 1))
            for ch, verses, block, url in chapters:
                for v in verses:
                    idx = len(self.verses)
                    lab = str(v["verse"]).replace("–", "-")
                    n0, n1, let = parse_label(lab)
                    rec = {"book": book, "ch": ch, "v": lab, "n0": n0, "n1": n1, "let": let,
                           "text": v["text"], "div": div, "block": block,
                           "url": (url.rstrip("/") + "/#v%s-%s" % (1 if (book, ch) in FIXED_CH_NAMES else ch, lab)) if url else ""}
                    self.verses.append(rec)
                    self.by_book[book].append(idx)
                    self.by_chapter.setdefault((book, ch), []).append(idx)
                    self.key.setdefault((book, ch, lab), idx)

    def label(self, idx):
        v = self.verses[idx]
        name = FIXED_CH_NAMES.get((v["book"], v["ch"]))
        if name:
            return f'{name} 1:{v["v"]}'
        return f'{v["book"]} {v["ch"]}:{v["v"]}'

    def chapter_name(self, book, ch):
        return FIXED_CH_NAMES.get((book, ch), f"{book} {ch}")

    # ---- reference handling -------------------------------------------------
    REF_RE = re.compile(r"^((?:[1-3] )?[A-Z][A-Za-z ]+?) (\d.*)$")

    def _find(self, book, ch, label, edge):
        idxs = self.by_chapter.get((book, ch))
        if not idxs:
            return None
        n, _, let = parse_label(label)
        if (book, ch, label) in self.key and edge == "start":
            return self.key[(book, ch, label)]
        if let:
            exact = [k for k in idxs if self.verses[k]["n0"] == n and self.verses[k]["let"] == let]
            if exact:
                return exact[0]
            plain = [k for k in idxs if self.verses[k]["n0"] <= n <= self.verses[k]["n1"]]
            if plain:
                return plain[0] if edge == "start" else plain[-1]
        cands = [k for k in idxs if self.verses[k]["n0"] <= n <= self.verses[k]["n1"]]
        if cands:
            if edge == "start":
                plain = [k for k in cands if not self.verses[k]["let"]]
                return (plain or cands)[0]
            return cands[-1]          # a bare number at range end includes its lettered continuations
        if edge == "start":
            later = [k for k in idxs if self.verses[k]["n0"] >= n]
            return later[0] if later else None
        earlier = [k for k in idxs if self.verses[k]["n1"] <= n and self.verses[k]["n0"] > 0]
        return earlier[-1] if earlier else None

    def expand(self, ref):
        """Expand a reference string to sorted verse indices. Returns (indices, problems)."""
        ref = ref.strip().replace("–", "-").replace("—", "-")
        m = self.REF_RE.match(ref)
        if not m:
            return [], ["unparsed:" + ref]
        book, rest = m.group(1).strip(), m.group(2)
        fixed = None
        if book in ALIASES:
            book, fixed = ALIASES[book]
        if book not in self.by_book:
            return [], ["unknown book:" + book]
        out, problems = set(), []
        cur_ch = None
        for seg in [s.strip() for s in rest.split(",") if s.strip()]:
            a, b = ([x.strip() for x in seg.split("-", 1)] if "-" in seg else (seg, None))
            if ":" in a:
                ca, va = a.split(":", 1); ca = int(ca)
            elif cur_ch is None:
                ca, va = int(a), None
            else:
                ca, va = cur_ch, a
            if b is None:
                cb, vb = ca, va
            elif ":" in b:
                cb, vb = b.split(":", 1); cb = int(cb)
            else:
                cb, vb = ca, b
                if re.fullmatch(r"[a-z]+", vb):
                    vb = str(parse_label(va)[0]) + vb
            cur_ch = cb
            if fixed is not None:          # Susanna 1:x -> Daniel 13:x
                ca = cb = fixed
            if va is None:
                out.update(self.by_chapter.get((book, ca), []))
                continue
            s = self._find(book, ca, va, "start")
            e = self._find(book, cb, vb, "end")
            if s is None or e is None:
                problems.append(f"unresolved:{book} {seg}")
                continue
            if e < s:
                problems.append(f"reversed:{book} {seg}")
                s, e = e, s
            out.update(range(s, e + 1))
        return sorted(out), problems


def load_catalogue():
    return json.load(open(REPO + "data/current/commands.json"))


def coverage(bible, recs):
    cov = collections.defaultdict(set)
    prim = collections.defaultdict(set)
    problems = []
    for r in recs:
        idxs, p = bible.expand(r["reference"])
        problems += [(r["id"], x) for x in p]
        for i in idxs:
            cov[i].add(r["id"]); prim[i].add(r["id"])
        for a in r.get("additional_scripture") or []:
            ref = a.get("reference") if isinstance(a, dict) else str(a)
            idxs, p = bible.expand(ref)
            problems += [(r["id"], x) for x in p]
            for i in idxs:
                cov[i].add(r["id"])
    return cov, prim, problems
