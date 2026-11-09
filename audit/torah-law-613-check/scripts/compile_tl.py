"""Compile the Torah Law (556) check: 613 matching, duplicates and labels."""
import json, sys, collections, os, re
sys.path.insert(0, "/home/claude/work")
from audit_lib import Bible
B = Bible()
W = "/home/claude/work"; R3 = f"{W}/round3"; OUT = f"{W}/audit/torah-laws"
os.makedirs(OUT, exist_ok=True)
recs = json.load(open("/home/claude/repos/laws-and-commands/data/current/commands.json")); byid = {r["id"]: r for r in recs}
ix = json.load(open(f"{R3}/index.json")); pairs = json.load(open(f"{R3}/pairs.json"))
m613 = {x["m"]: x for x in json.load(open(f"{R3}/m613.json"))}
PARTIAL = "--partial" in sys.argv


def load(b):
    p = f"{R3}/out/{b}.jsonl"
    if not os.path.exists(p): return []
    return [json.loads(l) for l in open(p) if l.strip() and not json.loads(l).get("done")]


def disp(i):
    v = B.verses[i]; return f'{v["book"]} {v["ch"]}:{v["v"]}'


TL = [r for r in recs if r["mosaic_type"] == "Law"]
TLids = {r["id"] for r in TL}
# ---------------- 613
M = []
for b in ("M1", "M2", "M3", "M4", "M5", "M6"): M += load(b)
Mby = {o["m"]: o for o in M}
if len(Mby) != 613 and not PARTIAL: sys.exit(f"613 results incomplete: {len(Mby)}")
def mkey(m): return (0 if m[0] == "P" else 1, int(m[1:]))
rows613 = []
for m in sorted(Mby, key=mkey):
    o = Mby[m]; x = m613[m]
    labels = [byid[r]["study_placement"] for r in o["records"] if r in byid]
    rows613.append({"m": m, "statement": o["statement"], "source": x["ref"], "saints": disp(x["idx"][0]) + (f" (+{len(x['idx']) - 1})" if len(x["idx"]) > 1 else ""),
                    "status": o["status"], "type": o["type"], "records": o["records"], "labels": labels, "mislabel": o["mislabel"],
                    "confidence": o["confidence"], "note": o.get("note", "")})
st = collections.Counter(r["status"] for r in rows613)
by_type = collections.Counter(r["type"] for r in rows613 if r["status"] == "other_mosaic")
tl_matched = collections.defaultdict(list)
for r in rows613:
    for rid in r["records"]:
        if rid in TLids: tl_matched[rid].append(r["m"])
multi_tl = [r for r in rows613 if sum(1 for x in r["records"] if x in TLids) > 1]
# ---------------- duplicates
D1 = {o["id"]: o for o in load("D1")}; D2 = {o["id"]: o for o in load("D2")}; L1 = {o["id"]: o for o in load("L1")}
dups = []
for k, o in list(D1.items()) + list(D2.items()):
    a, b = pairs[k]
    if o["verdict"] in ("duplicate", "overlap", "restatement"):
        dups.append({"id": k, "kind": {"duplicate": "same passage, same direction", "overlap": "same passage, one contains the other",
                                       "restatement": "same law in another passage"}[o["verdict"]],
                     "a": a, "b": b, "keep": o["keep"], "label_conflict": o["label_conflict"], "confidence": o["confidence"], "note": o["note"]})
label_conflicts = [{"id": k, "a": pairs[k][0], "b": pairs[k][1], "verdict": o["verdict"], "note": o["note"]}
                   for k, o in list(D1.items()) + list(D2.items()) if o.get("label_conflict")]
# ---------------- labels
relabel = [dict(o, current=byid[o["id"]]["study_placement"]) for o in L1.values() if o["verdict"] == "relabel"]
not_law = [dict(o, current=byid[o["id"]]["study_placement"]) for o in L1.values() if not o["is_law"] and byid[o["id"]]["mosaic_type"] == "Law"]
mis613 = [r for r in rows613 if r["mislabel"]]
# ---------------- what the count would be
tl_redundant = sorted({(d["b"] if d["keep"] == d["a"] else d["a"]) for d in dups if d["kind"] == "same passage, same direction" and d["keep"] != "both"
                       and (d["b"] if d["keep"] == d["a"] else d["a"]) in TLids})
to_other = sorted({o["id"] for o in relabel if byid[o["id"]]["mosaic_type"] == "Law" and o["suggest"] != "Torah Law"})
to_law = sorted({o["id"] for o in relabel if byid[o["id"]]["mosaic_type"] != "Law" and o["suggest"] == "Torah Law"} |
                {rid for r in mis613 for rid in r["records"][:1] if rid in byid and byid[rid]["mosaic_type"] != "Law"})
adjusted = len(TL) - len(tl_redundant) - len(to_other) + len(to_law)
summary = {
    "torah_law_records": len(TL), "by_book": collections.Counter(r["book"] for r in TL), "by_classification": collections.Counter(r["classification"] for r in TL),
    "ids": collections.Counter("AUD (completeness review)" if r["id"].startswith("AUD") else "C (original Torah requirements)" for r in TL),
    "mosaic_types": collections.Counter(r["mosaic_type"] for r in recs if r["mosaic_type"]),
    "613": {"status": st, "other_mosaic_by_type": by_type, "mislabel_flags": len(mis613), "torah_law_records_matched": len(tl_matched),
            "torah_law_records_unmatched": len(TL) - len(tl_matched), "commandments_with_several_torah_law_records": len(multi_tl)},
    "duplicates": collections.Counter(d["kind"] for d in dups), "label_conflicts": len(label_conflicts),
    "relabel": collections.Counter(f'{o["current"]} → {o["suggest"]}' for o in relabel), "torah_law_not_laws": len(not_law),
    "adjusted_count": {"current": len(TL), "redundant_duplicates": len(tl_redundant), "relabel_away": len(to_other), "relabel_to_law": len(to_law), "would_be": adjusted},
}
json.dump(rows613, open(f"{OUT}/maimonides-613.json", "w"), ensure_ascii=False, indent=1)
json.dump(dups, open(f"{OUT}/duplicates.json", "w"), ensure_ascii=False, indent=1)
json.dump({"relabel": relabel, "torah_law_not_laws": not_law, "613_mislabel_flags": mis613, "label_conflicts": label_conflicts},
          open(f"{OUT}/labels.json", "w"), ensure_ascii=False, indent=1)
json.dump({"tl_matched": tl_matched, "tl_redundant": tl_redundant, "to_other": to_other, "to_law": to_law}, open(f"{OUT}/count-workings.json", "w"), indent=1)
json.dump(summary, open(f"{OUT}/summary.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(summary, ensure_ascii=False, indent=1))
