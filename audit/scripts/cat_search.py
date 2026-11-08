"""Search the Saints.Bible catalogue (current, 4,999 records).

usage:
  python3 -I /home/claude/work/cat_search.py words <word> [<word> ...]   # all words must appear in title/reference/notes
  python3 -I /home/claude/work/cat_search.py at "Book ch:v[-v]"           # records whose primary or additional Scripture includes that range
  python3 -I /home/claude/work/cat_search.py book "Book" [ch]             # every record for a book (optionally one chapter)
Prints: id | reference | record type | origin | audience | title  [+ additional Scripture]
"""
import sys, json, re
sys.path.insert(0, "/home/claude/work")
from audit_lib import Bible, load_catalogue

recs = load_catalogue()


def show(r):
    add = "; ".join(a["reference"] for a in r.get("additional_scripture") or [])
    print(f'{r["id"]} | {r["reference"]} | {r["record_type"]} | {r["origin"]} | {r["audience"]} | {r["title"]}'
          + (f"  [+ {add}]" if add else ""))


mode = sys.argv[1] if len(sys.argv) > 1 else ""
if mode == "words":
    ws = [w.lower() for w in sys.argv[2:]]
    n = 0
    for r in recs:
        blob = " ".join(str(r.get(k, "")) for k in ("title", "reference", "context_note", "catalogue_audience", "study_placement", "topic")).lower()
        blob += " " + " ".join(a["reference"] for a in r.get("additional_scripture") or []).lower()
        if all(w in blob for w in ws):
            show(r); n += 1
            if n >= 60:
                print("… (more; refine the words)"); break
elif mode == "at":
    B = Bible()
    target, _ = B.expand(sys.argv[2])
    t = set(target)
    for r in recs:
        hit = False
        for ref in [r["reference"]] + [a["reference"] for a in r.get("additional_scripture") or []]:
            ii, _ = B.expand(ref)
            if t & set(ii):
                hit = True; break
        if hit:
            show(r)
elif mode == "book":
    book = sys.argv[2]
    ch = sys.argv[3] if len(sys.argv) > 3 else None
    for r in recs:
        refs = [r["reference"]] + [a["reference"] for a in r.get("additional_scripture") or []]
        if r["book"] == book or any(x.startswith(book + " ") for x in refs):
            if ch is None or any(re.match(re.escape(book) + r" " + ch + r":", x) or
                                 re.match(r"(Greek Psalm|Susanna|Bel and the Dragon) " + ch + r":", x) for x in refs):
                show(r)
else:
    print(__doc__)
