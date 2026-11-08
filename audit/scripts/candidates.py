"""Build the candidate passages for reviewer batches.

A verse is a candidate when it lacks an itemized record (no record of <= 8 verses
covers it) and either:
  - it has a directive signal (strong set), or
  - it has a precise wisdom form, or
  - it sits in a wisdom book (Proverbs, Ecclesiastes, Sirach, Wisdom of Solomon), or
  - it is in a New Testament letter / Revelation (read in full for maximum recall).
Outside the Law division, a verse covered by any record (even a broad one) is
treated as covered; inside the Law division (Genesis-Deuteronomy) a verse is
covered only if an itemized record (<= 8 verses) includes it, because the
catalogue itemizes each Torah requirement separately from its passage groups.
Candidates are grouped into passages (contiguous, merging gaps of 1 verse) and
given one verse of context on each side.
"""
import sys, json, re, collections
sys.path.insert(0, "/home/claude/work")
from audit_lib import *

B = Bible(); recs = load_catalogue()
S = {int(k): v for k, v in json.load(open("/home/claude/work/signals2.json")).items()}
STRONG = {"IMP", "JUSS", "PROH", "SHALL", "CASU", "COMM", "LEXIMP", "REQ", "SHALL2", "VOCIMP", "REPORTED"}
re_wp = re.compile(r"\b(better (?:is|are|a|an|the|to)?\b.*\bthan\b|blessed (?:is|are) (?:the|he|she|they|those|a|whoever|every)|"
                   r"happy (?:is|are) |cursed (?:is|be) (?:the|he|whoever|everyone|anyone)|woe to|woe unto|"
                   r"the fear of the Lord|fear of God|my son\b|^son,|a proverb|the wise\b|a wise man|a fool\b|the fool\b|"
                   r"the righteous (?:will|shall|is|are)|the wicked (?:will|shall|is|are))", re.I)
WISDOM_BOOKS = {"Proverbs", "Ecclesiastes", "Sirach", "Wisdom of Solomon"}
LAW = {"Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"}
NT_LETTERS = set(B.order[B.order.index("Romans"):])     # Romans .. Revelation

itemized, anycov, recs_at = set(), set(), collections.defaultdict(set)
for r in recs:
    for ref in [r["reference"]] + [a["reference"] for a in r["additional_scripture"]]:
        ii, _ = B.expand(ref)
        for i in ii:
            anycov.add(i); recs_at[i].add(r["id"])
            if len(ii) <= 8:
                itemized.add(i)


def is_candidate(i):
    v = B.verses[i]
    covered = (i in itemized) if v["book"] in LAW else (i in anycov)
    if covered:
        return None
    sig = set(S[i]["sig"])
    reasons = []
    if sig & STRONG:
        reasons.append("directive")
    if re_wp.search(v["text"]):
        reasons.append("wisdom-form")
    if v["book"] in WISDOM_BOOKS:
        reasons.append("wisdom-book")
    if v["book"] in NT_LETTERS:
        reasons.append("nt-letter")
    if not reasons:
        return None
    if v["book"] in LAW and i in anycov:
        reasons.append("broad-only")
    return reasons


cand = {}
for i in range(len(B.verses)):
    r = is_candidate(i)
    if r:
        cand[i] = r

# group into passages per chapter
passages = []
for (book, ch), idxs in B.by_chapter.items():
    run = []
    for i in idxs:
        if i in cand:
            if run and i - run[-1] > 2:
                passages.append(run); run = []
            run.append(i)
    if run:
        passages.append(run)

out = []
for n, run in enumerate(passages):
    chap = B.by_chapter[(B.verses[run[0]]["book"], B.verses[run[0]]["ch"])]
    lo, hi = chap.index(run[0]), chap.index(run[-1])
    ctx_lo, ctx_hi = max(0, lo - 1), min(len(chap) - 1, hi + 1)
    verses = []
    for k in chap[ctx_lo:ctx_hi + 1]:
        verses.append({"i": k, "ref": B.label(k), "text": B.verses[k]["text"],
                       "role": "candidate" if k in cand else "context",
                       "sig": [s for s in S[k]["sig"] if s != "ADDR_GOD"] if k in cand else [],
                       "why": cand.get(k, []),
                       "covered_by": sorted(recs_at.get(k, []))[:6]})
    out.append({"pid": f"P{n+1:05d}", "book": B.verses[run[0]]["book"], "ch": B.verses[run[0]]["ch"],
                "chapter_name": B.chapter_name(B.verses[run[0]]["book"], B.verses[run[0]]["ch"]),
                "first": B.label(run[0]), "last": B.label(run[-1]), "n_candidates": len([k for k in run if k in cand]),
                "verses": verses})
json.dump(out, open("/home/claude/work/passages.json", "w"), ensure_ascii=False)
bb = collections.Counter(B.verses[i]["book"] for i in cand)
print("candidate verses", len(cand), "passages", len(out))
print("words incl. context", sum(len(v["text"].split()) for p in out for v in p["verses"]))
for b in B.order:
    print(f"{b:20s} {bb.get(b,0):5d}  passages {sum(1 for p in out if p['book']==b)}")
