"""Find verses that received different decisions in different round-2 items."""
import json, sys, collections, glob, os
sys.path.insert(0, "/home/claude/work")
from audit_lib import Bible
B = Bible()
W = "/home/claude/work"
ix = json.load(open(f"{W}/round2/index.json"))
rows = []
for b in ix:
    p = f"{W}/round2/out/{b}.jsonl"
    if not os.path.exists(p): continue
    for l in open(p):
        if not l.strip(): continue
        o = json.loads(l)
        if o.get("done"): continue
        o["batch"] = b; rows.append(o)
by_v = collections.defaultdict(list)
for o in rows:
    d = o["decision"]
    if d == "no_record": continue
    idx, p = B.expand(o.get("reference", ""))
    tgt = o.get("existing_id") if d in ("record_extend", "record_parallel") else "NEW"
    for i in idx: by_v[i].append((o["item"], d, tgt, "main"))
    if d == "record_new":
        adds = list(o.get("additional_scripture") or [])
        if isinstance(o.get("additional"), str): adds += [x.strip() for x in o["additional"].split(";") if x.strip()]
        elif isinstance(o.get("additional"), list): adds += o["additional"]
        for a in adds:
            ref = a.get("reference") if isinstance(a, dict) else str(a)
            for i in B.expand(ref)[0]: by_v[i].append((o["item"], "new_additional", "NEW:" + o["item"], "add"))


def lab(i): v = B.verses[i]; return f'{v["book"]} {v["ch"]}:{v["v"]}'


groups = collections.OrderedDict()
for i in sorted(by_v):
    hits = by_v[i]
    items = {h[0] for h in hits}
    if len(items) < 2: continue
    kinds = {(h[1], h[2] if h[1] != "record_new" else "NEW:" + h[0]) for h in hits}
    if len(kinds) < 2: continue
    key = tuple(sorted(items))
    groups.setdefault(key, []).append(i)
out = []
for items, vs in groups.items():
    dd = [o for o in rows if o["item"] in items]
    out.append({"verses": f"{lab(vs[0])}" + (f" … {lab(vs[-1])}" if len(vs) > 1 else ""), "n": len(vs),
                "decisions": [{k: o.get(k) for k in ("item", "batch", "decision", "existing_id", "reference", "title", "record_type", "confidence", "reason", "additional_scripture") if o.get(k)} for o in dd]})
json.dump(out, open(f"{W}/round2/conflicts.json", "w"), ensure_ascii=False, indent=1)
print(len(rows), "decisions;", len(out), "conflict groups")
for g in out:
    print("\n==", g["verses"], f"({g['n']} verses)")
    for d in g["decisions"]:
        print("  ", d["item"], d["batch"], d["decision"], d.get("existing_id", ""), "|", d.get("reference"), "|", (d.get("title") or "")[:60], "|", d.get("confidence"), "|", (d.get("reason") or "")[:150], ("| add: " + json.dumps(d["additional_scripture"], ensure_ascii=False)[:120]) if d.get("additional_scripture") else "")
