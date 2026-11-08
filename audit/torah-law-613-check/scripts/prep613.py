"""Build review batches pairing Maimonides' 613 commandments with candidate catalogue records."""
import json, re, sys, os, collections
sys.path.insert(0, "/home/claude/work")
from audit_lib import Bible
B = Bible()
W = "/home/claude/work"; OUT = f"{W}/round3"
os.makedirs(f"{OUT}/batches", exist_ok=True); os.makedirs(f"{OUT}/out", exist_ok=True)
recs = json.load(open("/home/claude/repos/laws-and-commands/data/current/commands.json"))
M = json.load(open(f"{W}/check613.json"))
BK = {"Ex": "Exodus", "Exo": "Exodus", "Lev": "Leviticus", "Num": "Numbers", "Deut": "Deuteronomy", "Deu": "Deuteronomy", "Gen": "Genesis"}


def parse(ref):
    m = re.search(r"\(Saints ([^)]+)\)", ref)
    base = re.sub(r"\s*\(Saints [^)]+\)", "", ref)
    idxs, last_book = [], None
    for part in re.split(r";\s*", base):
        mm = re.match(r"(?:(\w+)\.?\s+)?(\d.*)$", part.strip())
        book = BK.get(mm.group(1), last_book) if mm.group(1) else last_book
        last_book = book
        body = mm.group(2)
        if m:  # Saints override for this reference (single verse)
            body = m.group(1)
        ii, p = B.expand(f"{book} {body}")
        idxs += ii
    return idxs, last_book


def label(r):
    return r.get("study_placement") or r.get("collection")


span = collections.defaultdict(list)   # verse -> records (primary or additional)
first = {}
for r in recs:
    refs = [r["reference"]] + [a["reference"] for a in r.get("additional_scripture") or []]
    for k, ref in enumerate(refs):
        ii, _ = B.expand(ref)
        for i in ii: span[i].append((r["id"], "primary" if k == 0 else "additional", len(ii)))
    ii, _ = B.expand(r["reference"])
    if ii: first[r["id"]] = ii
byid = {r["id"]: r for r in recs}
TORAH = {"Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"}

items = []
changed = []
for x in M:
    idx, book = parse(x["ref"])
    if sorted(idx) != sorted(x["idx"]): changed.append((x["mitzva"], x["ref"], len(x["idx"]), len(idx)))
    idx = sorted(set(idx))
    vs = set(idx)
    near = set()
    for i in idx:
        for j in range(i - 2, i + 3):
            if 0 <= j < len(B.verses) and B.verses[j]["book"] == B.verses[i]["book"] and B.verses[j]["ch"] == B.verses[i]["ch"]:
                near.add(j)
    cands = {}
    for j in sorted(near):
        for rid, kind, n in span.get(j, []):
            hit = j in vs
            prev = cands.get(rid)
            score = (0 if hit else 1, n)
            if prev is None or score < prev[0]:
                cands[rid] = (score, kind, n, hit)
    order = sorted(cands.items(), key=lambda kv: (kv[1][0], first.get(kv[0], [0])[0]))[:22]
    items.append({"m": x["mitzva"], "ref": x["ref"], "idx": idx, "cands": [(rid, v[1], v[2], v[3]) for rid, v in order]})

json.dump([{"m": it["m"], "ref": it["ref"], "idx": it["idx"]} for it in items], open(f"{OUT}/m613.json", "w"))
print("references re-parsed differently from stored:", changed)


def disp(i):
    v = B.verses[i]; return f'{v["book"]} {v["ch"]}:{v["v"]}'


def block(it):
    L = [f"### {it['m']} · source {it['ref']}"]
    show = it["idx"] if len(it["idx"]) <= 6 else it["idx"][:3] + it["idx"][-2:]
    for i in show:
        L.append(f"   {disp(i)} {B.verses[i]['text']}")
    if len(it["idx"]) > 6: L.append(f"   … ({len(it['idx'])} verses in all)")
    if not it["cands"]: L.append("   candidates: none within two verses")
    for rid, kind, n, hit in it["cands"]:
        r = byid[rid]
        where = ("holds the source verse" if hit else "nearby") + (" as Additional Scripture" if kind == "additional" else "")
        L.append(f"   - {rid} | {r['reference']} | {label(r)} | {r['record_type']} | {r['title']} ({where}; {n} verses)")
    return "\n".join(L)


items.sort(key=lambda it: it["idx"][0] if it["idx"] else 10 ** 9)
n = len(items); k = 6; size = (n + k - 1) // k
index = {}
for b in range(k):
    chunk = items[b * size:(b + 1) * size]
    name = f"M{b + 1}"
    index[name] = [it["m"] for it in chunk]
    open(f"{OUT}/batches/{name}.md", "w").write(
        f"# 613 batch {name}: {len(chunk)} commandments, {disp(chunk[0]['idx'][0])} to {disp(chunk[-1]['idx'][0])}\n\n" + "\n\n".join(block(it) for it in chunk) + "\n")
    print(name, len(chunk), disp(chunk[0]["idx"][0]), "→", disp(chunk[-1]["idx"][0]))
json.dump(index, open(f"{OUT}/index.json", "w"), indent=0)
