import sys, re, json, collections
sys.path.insert(0, "/home/claude/work")
from audit_lib import *
B = Bible(); recs = load_catalogue()
BK = {"Ex": "Exodus", "Exo": "Exodus", "Lev": "Leviticus", "Num": "Numbers", "Deut": "Deuteronomy", "Deu": "Deuteronomy", "Gen": "Genesis"}
span = {}
for r in recs:
    for ref in [r["reference"]] + [a["reference"] for a in r["additional_scripture"]]:
        ii, _ = B.expand(ref)
        for i in ii:
            span.setdefault(i, []).append((len(ii), r["id"]))
byid = {r["id"]: r for r in recs}
rows = []
for line in open("/home/claude/work/ext/rambam613_refs.txt"):
    if line.startswith("#"): continue
    for item in re.split(r",\s*(?=[PN]\d+=)", line.strip()):
        if "=" not in item: continue
        num, ref = item.split("=", 1)
        idxs = []
        last_book = None
        for part in re.split(r";\s*", ref):
            m = re.match(r"(?:(\w+)\.?\s+)?(\d.*)$", part.strip())
            book = BK.get(m.group(1), last_book) if m.group(1) else last_book
            last_book = book
            ii, p = B.expand(f"{book} {m.group(2)}")
            idxs += ii
        fine = sorted({rid for i in idxs for (n, rid) in span.get(i, []) if n <= 8})
        anyc = sorted({rid for i in idxs for (n, rid) in span.get(i, [])})
        rows.append({"mitzva": num, "ref": ref, "idx": idxs, "fine": fine, "any": anyc})
st = collections.Counter("itemized" if r["fine"] else "broad-only" if r["any"] else "none" for r in rows)
print(len(rows), st)
json.dump(rows, open("/home/claude/work/check613.json", "w"))
for r in rows:
    if not r["fine"]:
        t = B.verses[r["idx"][0]]["text"][:150] if r["idx"] else "?"
        print(f'{r["mitzva"]:5s} {r["ref"]:18s} {"broad" if r["any"] else "NONE":5s} | {t}')
