import json, sys, re, os
sys.path.insert(0, "/home/claude/work")
from audit_lib import Bible
B = Bible()
O = "/home/claude/work/round3"
recs = json.load(open("/home/claude/repos/laws-and-commands/data/current/commands.json")); byid = {r["id"]: r for r in recs}
C = json.load(open(f"{O}/tl_candidates.json"))
def txt(r, k=4):
    ii = B.expand(r["reference"])[0]
    s = [f'      {B.verses[i]["book"]} {B.verses[i]["ch"]}:{B.verses[i]["v"]} {B.verses[i]["text"]}' for i in ii[:k]]
    if len(ii) > k: s.append(f"      … ({len(ii)} verses)")
    return s
def rec(r, tag):
    add = "; ".join(a["reference"] for a in r.get("additional_scripture") or [])
    return [f'   {tag} {r["id"]} | {r["reference"]} | {r["study_placement"]} | {r["title"]} | classification: {r["classification"]} | topic: {r["topic"]}' + (f" | + {add}" if add else "")]
def write(name, title, items):
    open(f"{O}/batches/{name}.md", "w").write(f"# {title}: {len(items)} items\n\n" + "\n\n".join(items) + "\n")
idx = json.load(open(f"{O}/index.json"))
# D1 same-passage
items, ids = [], []
for n, p in enumerate(sorted(C["same_passage"], key=lambda p: (B.expand(byid[p["a"]]["reference"])[0][0], p["a"], p["b"])), 1):
    a, b = byid[p["a"]], byid[p["b"]]
    L = [f"### D{n:03d} · same passage ({p['overlap']} shared verse{'s' if p['overlap'] > 1 else ''})"] + rec(a, "A") + rec(b, "B")
    L += ["   text:"] + txt(a if len(B.expand(a["reference"])[0]) >= len(B.expand(b["reference"])[0]) else b)
    items.append("\n".join(L)); ids.append(f"D{n:03d}")
write("D1", "Same-passage pairs", items); idx["D1"] = ids
pairs = {f"D{n:03d}": (p["a"], p["b"]) for n, p in enumerate(sorted(C["same_passage"], key=lambda p: (B.expand(byid[p["a"]]["reference"])[0][0], p["a"], p["b"])), 1)}
# D2 cross-passage
items, ids = [], []
for n, p in enumerate(C["cross_passage"], 1):
    a, b = byid[p["a"]], byid[p["b"]]
    L = [f"### X{n:03d} · different passages (text similarity {p['sim']}{'; already linked as Additional Scripture' if p['linked_as_additional'] else ''})"] + rec(a, "A") + txt(a, 3) + rec(b, "B") + txt(b, 3)
    items.append("\n".join(L)); ids.append(f"X{n:03d}")
    pairs[f"X{n:03d}"] = (p["a"], p["b"])
write("D2", "Cross-passage pairs", items); idx["D2"] = ids
# L1 label review
TB = {"Exodus", "Leviticus", "Numbers", "Deuteronomy"}
sel = []
sel += [(i, "Torah Law with a procedural title") for i in C["law_procedural_titles"]]
sel += [(i, "Instruction or Command with a prohibition title") for i in C["other_prohibition_titles"]]
sel += [(r["id"], "Law-type historical direction record without a Mosaic type") for r in recs if r["book"] in TB and not r["mosaic_type"] and r["record_type"] == "Law" and r["origin"].startswith("Heavenly") and r["study_placement"] in ("Torah · Historical direction", "Torah · Historical direction study")]
sel += [(r["id"], "Torah Law added by the completeness review") for r in recs if r["mosaic_type"] == "Law" and r["id"].startswith("AUD")]
seen, items, ids = set(), [], []
for rid, why in sel:
    if rid in seen: continue
    seen.add(rid); r = byid[rid]
    L = [f"### {rid} · {why}"] + rec(r, "") + txt(r, 4)
    items.append("\n".join(L)); ids.append(rid)
write("L1", "Label review", items); idx["L1"] = ids
json.dump(idx, open(f"{O}/index.json", "w"), indent=0)
json.dump(pairs, open(f"{O}/pairs.json", "w"))
print({k: len(v) for k, v in idx.items()})
